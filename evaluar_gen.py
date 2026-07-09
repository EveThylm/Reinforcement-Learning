import pygame
import sys
import time
import json
import constantes
from personaje import Personaje
from mapa import crear_mapa, WAYPOINT_Y_VALUES
from fitness import calcular_fitness


def cargar_animaciones():
    animaciones = []
    for i in range(7):
        img = pygame.image.load(rf"assets\images\characters\player\Player_{i}.png")
        w, h = img.get_width(), img.get_height()
        img = pygame.transform.scale(img, (w * constantes.scala_personaje, h * constantes.scala_personaje))
        animaciones.append(img)
    return animaciones


def evaluar_con_render(secuencia, frames_por_accion=30, velocidad=0.3, repeticiones=1):
    pygame.init()
    ventana = pygame.display.set_mode((constantes.ancho_ventana, constantes.alto_ventana))
    pygame.display.set_caption("Jump King - Evaluacion Evolutiva")
    reloj = pygame.time.Clock()

    animaciones = cargar_animaciones()
    mapa = crear_mapa()

    for rep in range(repeticiones):
        print(f"\n=== Repeticion {rep + 1}/{repeticiones} ===")

        jugador = Personaje(constantes.spawn_x, constantes.spawn_y, animaciones)
        jugador.on_ground = True
        camara_y = 0

        accion_idx = 0
        frame_en_accion = 0
        altura_maxima_suelo = constantes.suelo_y
        altura_maxima_aires = constantes.suelo_y
        pasos_en_suelo = 0
        waypoints_visitados = set()
        altura_actual_suelo = constantes.suelo_y
        consecutive_idle = 0
        total_idle_frames = 0
        prev_x = jugador.forma.x
        total_stuck_frames = 0
        prev_y = jugador.forma.centery
        total_fallback_frames = 0

        ejecutando = True
        while ejecutando:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return
                    if event.key == pygame.K_r:
                        jugador = Personaje(constantes.spawn_x, constantes.spawn_y, animaciones)
                        jugador.on_ground = True
                        camara_y = 0
                        accion_idx = 0
                        frame_en_accion = 0
                        altura_maxima_suelo = constantes.suelo_y
                        altura_maxima_aires = constantes.suelo_y
                        pasos_en_suelo = 0
                        waypoints_visitados = set()
                        altura_actual_suelo = constantes.suelo_y
                        consecutive_idle = 0
                        total_idle_frames = 0
                        prev_x = jugador.forma.x
                        total_stuck_frames = 0
                        prev_y = jugador.forma.centery
                        total_fallback_frames = 0
                        print("Reiniciando...")

            accion = secuencia[accion_idx] if accion_idx < len(secuencia) else 0

            if jugador.on_ground:
                if accion == 1:
                    jugador.velocidad_y = -constantes.fuerza_salto_max
                    jugador.velocidad_x = -constantes.vx_salto
                    jugador.on_ground = False
                elif accion == 2:
                    jugador.velocidad_y = -constantes.fuerza_salto_max
                    jugador.velocidad_x = constantes.vx_salto
                    jugador.on_ground = False
                elif accion == 3:
                    jugador.velocidad_y = -12
                    jugador.velocidad_x = -constantes.vx_salto
                    jugador.on_ground = False
                elif accion == 4:
                    jugador.velocidad_y = -12
                    jugador.velocidad_x = constantes.vx_salto
                    jugador.on_ground = False

            jugador.aplicar_gravedad()
            jugador.forma.y += jugador.velocidad_y

            jugador.on_ground = False
            pies = pygame.Rect(jugador.forma.x, jugador.forma.bottom, jugador.forma.width, 4)
            for plat in mapa.plataformas:
                if pies.colliderect(plat.rect):
                    jugador.on_ground = True
                    if jugador.velocidad_y >= 0:
                        jugador.forma.bottom = plat.rect.top
                        jugador.velocidad_y = 0
                        jugador.velocidad_x = 0
                    break

            jugador.forma.x += jugador.velocidad_x

            for plat in mapa.plataformas:
                if jugador.forma.colliderect(plat.rect):
                    if jugador.velocidad_y < 0:
                        jugador.forma.top = plat.rect.bottom
                        jugador.velocidad_y = 0
                    elif not jugador.on_ground:
                        if jugador.velocidad_x > 0:
                            jugador.forma.right = plat.rect.left
                        elif jugador.velocidad_x < 0:
                            jugador.forma.left = plat.rect.right

            if jugador.forma.left < 0:
                jugador.forma.left = 0
            if jugador.forma.right > constantes.ancho_ventana:
                jugador.forma.right = constantes.ancho_ventana

            if jugador.forma.top > constantes.umbral_caida:
                jugador.forma.center = (constantes.spawn_x, constantes.spawn_y)
                jugador.velocidad_y = 0
                jugador.velocidad_x = 0
                jugador.on_ground = True

            jugador.update()

            target = jugador.forma.centery - constantes.alto_ventana // 2
            camara_y += (target - camara_y) * 0.1

            altura_actual = jugador.forma.centery

            if altura_actual < altura_maxima_aires:
                altura_maxima_aires = altura_actual

            if jugador.on_ground:
                pasos_en_suelo += 1
                if pasos_en_suelo >= 3 and altura_actual < altura_maxima_suelo:
                    altura_maxima_suelo = altura_actual
                altura_actual_suelo = altura_actual
            else:
                pasos_en_suelo = 0

            for i, wp_y in enumerate(WAYPOINT_Y_VALUES):
                if altura_actual <= wp_y + 10 and jugador.on_ground:
                    waypoints_visitados.add(i)

            if accion == 0:
                consecutive_idle += 1
                if consecutive_idle >= 3:
                    total_idle_frames += 1
            else:
                consecutive_idle = 0

            if accion in (1, 2, 3, 4):
                if jugador.forma.x == prev_x:
                    total_stuck_frames += 1
            prev_x = jugador.forma.x

            if altura_actual > prev_y:
                total_fallback_frames += 1
            prev_y = altura_actual

            frame_en_accion += 1
            if frame_en_accion >= frames_por_accion:
                frame_en_accion = 0
                accion_idx += 1

            ventana.fill(constantes.color_bg)
            for plat in mapa.plataformas:
                rect_dibujar = plat.rect.copy()
                rect_dibujar.y -= camara_y
                pygame.draw.rect(ventana, (100, 200, 100), rect_dibujar)
            jugador.dibujar(ventana, camara_y)

            font = pygame.font.SysFont(None, 30)
            progreso_suelo = max(0, min(100, int((constantes.suelo_y - altura_maxima_suelo) / (constantes.suelo_y - 50) * 100)))
            progreso_aire = max(0, min(100, int((constantes.suelo_y - altura_maxima_aires) / (constantes.suelo_y - 50) * 100)))
            fitness_actual, _ = calcular_fitness(
                altura_maxima_suelo, altura_maxima_aires,
                waypoints_visitados, altura_actual_suelo,
                total_idle_frames, total_stuck_frames,
                total_fallback_frames
            )
            accion_nombre = ["Idle", "Izq Full", "Der Full", "Izq 3/4", "Der 3/4"][accion]
            texto = font.render(
                f"Accion: {accion_nombre} ({accion_idx+1}/{len(secuencia)}) | Suelo: {progreso_suelo}% | Aire: {progreso_aire}% | WP: {len(waypoints_visitados)}/{len(WAYPOINT_Y_VALUES)} | Fitness: {fitness_actual:.0f}",
                True, (255, 255, 255)
            )
            ventana.blit(texto, (10, 10))
            texto2 = font.render("ESC: Salir | R: Reiniciar", True, (180, 180, 180))
            ventana.blit(texto2, (10, 40))
            pygame.display.update()
            reloj.tick(int(velocidad * 60))

            if accion_idx >= len(secuencia):
                fitness_final, datos = calcular_fitness(
                    altura_maxima_suelo, altura_maxima_aires,
                    waypoints_visitados, altura_actual_suelo,
                    total_idle_frames, total_stuck_frames,
                    total_fallback_frames
                )
                print(f"\n=== FITNESS BREAKDOWN ===")
                print(f"  Suelo:     {datos['suelo_px']:.0f}px x 1.0  = {datos['suelo']:.1f}")
                print(f"  Aire:      {datos['aire_px']:.0f}px x 0.5 = {datos['aire']:.1f}")
                print(f"  Waypoints: {datos['waypoints_count']}/{datos['waypoints_total']} x 200 = {datos['waypoints']:.1f}")
                print(f"  Caida:     {datos['caida_px']:.0f}px x -2   = {-datos['caida'] * 2:.1f}")
                print(f"  Idle:      {datos['idle_frames']} frames x -0.5 = {-datos['idle_penalty']:.1f}")
                print(f"  Wall:      {datos['wall_hits']} hits x -1.0  = {-datos['wall_penalty']:.1f}")
                print(f"  Fallback:  {datos['fallback_frames']} frames x -1.0 = {-datos['fallback_penalty']:.1f}")
                print(f"  {'='*30}")
                print(f"  TOTAL FITNESS:          = {fitness_final:.1f}")
                print(f"  Suelo: {progreso_suelo}% ({constantes.suelo_y - altura_maxima_suelo:.0f}px) | Aire: {progreso_aire}% ({constantes.suelo_y - altura_maxima_aires:.0f}px)")
                time.sleep(2)
                ejecutando = False

    pygame.quit()


def cargar_secuencia():
    try:
        with open("mejor_secuencia.txt", "r") as f:
            secuencia = json.load(f)
            print(f"Secuencia cargada ({len(secuencia)} acciones)")
            return secuencia
    except FileNotFoundError:
        print("No se encontro mejor_secuencia.txt")
        print("Ejecuta primero: python evolutivo.py")
        return None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Evaluar mejor secuencia evolutiva")
    parser.add_argument("--velocidad", type=float, default=0.5)
    parser.add_argument("--repeticiones", type=int, default=1)
    parser.add_argument("--frames", type=int, default=30)
    args = parser.parse_args()

    secuencia = cargar_secuencia()
    if secuencia:
        evaluar_con_render(secuencia, args.frames, args.velocidad, args.repeticiones)
