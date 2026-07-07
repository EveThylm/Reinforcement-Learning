import pygame
import sys
import time
import constantes
from personaje import Personaje
from plataforma import Plataforma
from nivel import Nivel


def cargar_mapa():
    return Nivel([
        Plataforma(0, 2950, 800, 50),
        Plataforma(300, 2840, 250, 20),
        Plataforma(50, 2750, 180, 20),
        Plataforma(450, 2750, 180, 20),
        Plataforma(200, 2660, 140, 20),
        Plataforma(500, 2660, 120, 20),
        Plataforma(100, 2570, 150, 20),
        Plataforma(30, 2480, 130, 20),
        Plataforma(200, 2400, 120, 20),
        Plataforma(450, 2470, 120, 20),
        Plataforma(550, 2380, 130, 20),
        Plataforma(300, 2310, 140, 20),
        Plataforma(500, 2300, 110, 20),
        Plataforma(620, 2220, 120, 20),
        Plataforma(450, 2150, 110, 20),
        Plataforma(250, 2100, 120, 20),
        Plataforma(400, 2010, 120, 20),
        Plataforma(180, 1930, 130, 20),
        Plataforma(400, 1850, 120, 20),
        Plataforma(180, 1770, 130, 20),
        Plataforma(400, 1690, 120, 20),
        Plataforma(180, 1610, 140, 20),
        Plataforma(380, 1530, 140, 20),
        Plataforma(180, 1450, 140, 20),
        Plataforma(380, 1370, 140, 20),
        Plataforma(180, 1290, 130, 20),
        Plataforma(380, 1210, 130, 20),
        Plataforma(180, 1130, 130, 20),
        Plataforma(380, 1050, 130, 20),
        Plataforma(180, 970, 130, 20),
        Plataforma(380, 890, 130, 20),
        Plataforma(180, 810, 130, 20),
        Plataforma(380, 730, 130, 20),
        Plataforma(450, 650, 120, 20),
        Plataforma(200, 570, 120, 20),
        Plataforma(450, 490, 120, 20),
        Plataforma(200, 410, 120, 20),
        Plataforma(350, 340, 100, 20),
        Plataforma(150, 270, 100, 20),
        Plataforma(400, 200, 100, 20),
        Plataforma(250, 130, 100, 20),
        Plataforma(300, 50, 200, 30),
    ])


def cargar_animaciones():
    animaciones = []
    for i in range(7):
        img = pygame.image.load(rf"assets\images\characters\player\Player_{i}.png")
        w, h = img.get_width(), img.get_height()
        img = pygame.transform.scale(img, (w * constantes.scala_personaje, h * constantes.scala_personaje))
        animaciones.append(img)
    return animaciones


def evaluar_con_render(secuencia, frames_por_accion=20, velocidad=0.3, repeticiones=1):
    """Evalúa una secuencia con render visual."""
    pygame.init()
    ventana = pygame.display.set_mode((constantes.ancho_ventana, constantes.alto_ventana))
    pygame.display.set_caption("Jump King - Evaluacion Evolutiva")
    reloj = pygame.time.Clock()

    animaciones = cargar_animaciones()
    mapa = cargar_mapa()

    for rep in range(repeticiones):
        print(f"\n=== Repeticion {rep + 1}/{repeticiones} ===")

        jugador = Personaje(60, 2930, animaciones)
        jugador.on_ground = True
        camara_y = 0

        cargando = False
        tiempo_carga = 0
        direccion = 0
        accion_idx = 0
        frame_en_accion = 0
        altura_maxima = 2950
        prev_y = jugador.forma.centery

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
                        jugador = Personaje(60, 2930, animaciones)
                        jugador.on_ground = True
                        camara_y = 0
                        cargando = False
                        tiempo_carga = 0
                        accion_idx = 0
                        frame_en_accion = 0
                        prev_y = jugador.forma.centery
                        print("Reiniciando...")

            # Obtener accion actual
            if accion_idx < len(secuencia):
                accion = secuencia[accion_idx]
            else:
                accion = 0

            # Procesar accion
            if accion == 0:
                if cargando:
                    fuerza = min(tiempo_carga * (constantes.fuerza_salto_max / constantes.tiempo_carga_max), constantes.fuerza_salto_max)
                    jugador.velocidad_y = -fuerza
                    jugador.velocidad_x = direccion * constantes.velocidad
                    jugador.on_ground = False
                    cargando = False
                    tiempo_carga = 0
            elif accion == 1:
                if jugador.on_ground and not cargando:
                    cargando = True
                    tiempo_carga = 0
                    direccion = -1
            elif accion == 2:
                if jugador.on_ground and not cargando:
                    cargando = True
                    tiempo_carga = 0
                    direccion = 1
            elif accion == 3:
                if jugador.on_ground and not cargando:
                    cargando = True
                    tiempo_carga = 0
                    import random
                    direccion = random.choice([-1, 1])

            # Incrementar carga
            if cargando:
                tiempo_carga += 1
                if tiempo_carga >= constantes.tiempo_carga_max:
                    fuerza = constantes.fuerza_salto_max
                    jugador.velocidad_y = -fuerza
                    jugador.velocidad_x = direccion * constantes.velocidad
                    jugador.on_ground = False
                    cargando = False
                    tiempo_carga = 0

            # Fisica
            jugador.aplicar_gravedad()
            jugador.forma.y += jugador.velocidad_y

            # Detectar suelo
            jugador.on_ground = False
            for plat in mapa.plataformas:
                if (prev_y <= plat.rect.top and jugador.forma.bottom >= plat.rect.top and
                    jugador.velocidad_y >= 0 and
                    jugador.forma.right > plat.rect.left and 
                    jugador.forma.left < plat.rect.right):
                    jugador.forma.bottom = plat.rect.top
                    jugador.velocidad_y = 0
                    jugador.velocidad_x = 0
                    jugador.on_ground = True
                    break

            prev_y = jugador.forma.centery

            # Movimiento horizontal (siempre)
            jugador.forma.x += jugador.velocidad_x

            # Limites
            if jugador.forma.left < 0:
                jugador.forma.left = 0
            if jugador.forma.right > constantes.ancho_ventana:
                jugador.forma.right = constantes.ancho_ventana

            # Respawn
            if jugador.forma.top > 3100:
                jugador.forma.center = (60, 2930)
                jugador.velocidad_y = 0
                jugador.velocidad_x = 0
                jugador.on_ground = True
                cargando = False
                tiempo_carga = 0
                prev_y = jugador.forma.centery

            jugador.update()

            # Camara
            target = jugador.forma.centery - constantes.alto_ventana // 2
            camara_y += (target - camara_y) * 0.1

            # Actualizar altura
            if jugador.forma.centery < altura_maxima:
                altura_maxima = jugador.forma.centery

            # Avanzar accion
            frame_en_accion += 1
            if frame_en_accion >= frames_por_accion:
                frame_en_accion = 0
                accion_idx += 1

            # Dibujar
            ventana.fill(constantes.color_bg)

            for plat in mapa.plataformas:
                rect_dibujar = plat.rect.copy()
                rect_dibujar.y -= camara_y
                pygame.draw.rect(ventana, (100, 200, 100), rect_dibujar)

            jugador.dibujar(ventana, camara_y)

            # HUD
            font = pygame.font.SysFont(None, 30)
            progreso = max(0, min(100, int((2950 - altura_maxima) / (2950 - 50) * 100)))
            accion_nombre = ["Idle", "Izq", "Der", "Rand"][accion]
            texto = font.render(
                f"Accion: {accion_nombre} ({accion_idx+1}/{len(secuencia)}) | Progreso: {progreso}% | Altura: {2950 - altura_maxima:.0f}px",
                True, (255, 255, 255)
            )
            ventana.blit(texto, (10, 10))

            texto2 = font.render("ESC: Salir | R: Reiniciar", True, (180, 180, 180))
            ventana.blit(texto2, (10, 40))

            pygame.display.update()
            reloj.tick(int(velocidad * 60))

            # Terminar si completo la secuencia
            if accion_idx >= len(secuencia):
                print(f"Secuencia completada. Altura maxima: {2950 - altura_maxima:.0f}px | Progreso: {progreso}%")
                time.sleep(2)
                ejecutando = False

    pygame.quit()


def cargar_secuencia():
    """Carga la secuencia desde el archivo."""
    try:
        with open("mejor_secuencia.txt", "r") as f:
            secuencia_str = f.read().strip()
            secuencia = eval(secuencia_str)
            print(f"Secuencia cargada ({len(secuencia)} acciones)")
            return secuencia
    except FileNotFoundError:
        print("No se encontro mejor_secuencia.txt")
        print("Ejecuta primero: python evolutivo.py")
        return None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Evaluar mejor secuencia evolutiva")
    parser.add_argument("--velocidad", type=float, default=0.5, help="Velocidad de visualizacion")
    parser.add_argument("--repeticiones", type=int, default=1, help="Numero de repeticiones")
    parser.add_argument("--frames", type=int, default=20, help="Frames por accion")
    args = parser.parse_args()

    secuencia = cargar_secuencia()

    if secuencia:
        evaluar_con_render(secuencia, args.frames, args.velocidad, args.repeticiones)
