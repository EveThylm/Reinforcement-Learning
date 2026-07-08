import pygame
import sys
import time
import json
import constantes
from personaje import Personaje
from mapa import crear_mapa


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
        altura_maxima = constantes.suelo_y

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

            if jugador.forma.centery < altura_maxima:
                altura_maxima = jugador.forma.centery

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
            progreso = max(0, min(100, int((constantes.suelo_y - altura_maxima) / (constantes.suelo_y - 50) * 100)))
            accion_nombre = ["Idle", "Izq Full", "Der Full", "Izq 3/4", "Der 3/4"][accion]
            texto = font.render(
                f"Accion: {accion_nombre} ({accion_idx+1}/{len(secuencia)}) | Progreso: {progreso}% | Altura: {constantes.suelo_y - altura_maxima:.0f}px",
                True, (255, 255, 255)
            )
            ventana.blit(texto, (10, 10))
            texto2 = font.render("ESC: Salir | R: Reiniciar", True, (180, 180, 180))
            ventana.blit(texto2, (10, 40))
            pygame.display.update()
            reloj.tick(int(velocidad * 60))

            if accion_idx >= len(secuencia):
                print(f"Secuencia completada. Altura maxima: {constantes.suelo_y - altura_maxima:.0f}px | Progreso: {progreso}%")
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
