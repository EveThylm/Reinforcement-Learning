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

        accion_idx = 0
        frame_en_accion = 0
        altura_maxima = 2950

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
                        accion_idx = 0
                        frame_en_accion = 0
                        print("Reiniciando...")

            accion = secuencia[accion_idx] if accion_idx < len(secuencia) else 0

            # Saltos directos
            if jugador.on_ground:
                if accion == 1:
                    jugador.velocidad_y = -constantes.fuerza_salto_max
                    jugador.velocidad_x = -8
                    jugador.on_ground = False
                elif accion == 2:
                    jugador.velocidad_y = -constantes.fuerza_salto_max
                    jugador.velocidad_x = 8
                    jugador.on_ground = False

            # Fisica
            jugador.aplicar_gravedad()
            prev_y = jugador.forma.centery
            jugador.forma.y += jugador.velocidad_y

            # Colision vertical
            landed = False
            for plat in mapa.plataformas:
                if jugador.forma.colliderect(plat.rect):
                    if jugador.velocidad_y > 0 and prev_y <= plat.rect.top + 5:
                        jugador.forma.bottom = plat.rect.top
                        jugador.velocidad_y = 0
                        jugador.velocidad_x = 0
                        jugador.on_ground = True
                        landed = True
                    elif jugador.velocidad_y < 0:
                        jugador.forma.top = plat.rect.bottom
                        jugador.velocidad_y = 0
                    break
            
            if not landed and jugador.velocidad_y > 0:
                jugador.on_ground = False

            # Movimiento horizontal
            jugador.forma.x += jugador.velocidad_x

            # Colision horizontal
            for plat in mapa.plataformas:
                if jugador.forma.colliderect(plat.rect):
                    if not jugador.on_ground:
                        if jugador.velocidad_x > 0:
                            jugador.forma.right = plat.rect.left
                        elif jugador.velocidad_x < 0:
                            jugador.forma.left = plat.rect.right
                    jugador.velocidad_x = 0
                    break

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

            jugador.update()

            # Camara
            target = jugador.forma.centery - constantes.alto_ventana // 2
            camara_y += (target - camara_y) * 0.1

            if jugador.forma.centery < altura_maxima:
                altura_maxima = jugador.forma.centery

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

            font = pygame.font.SysFont(None, 30)
            progreso = max(0, min(100, int((2950 - altura_maxima) / (2950 - 50) * 100)))
            accion_nombre = ["Idle", "IzqS", "DerS", "IzqM", "DerM", "IzqF", "DerF"][accion]
            texto = font.render(
                f"Accion: {accion_nombre} ({accion_idx+1}/{len(secuencia)}) | Progreso: {progreso}% | Altura: {2950 - altura_maxima:.0f}px",
                True, (255, 255, 255)
            )
            ventana.blit(texto, (10, 10))
            texto2 = font.render("ESC: Salir | R: Reiniciar", True, (180, 180, 180))
            ventana.blit(texto2, (10, 40))
            pygame.display.update()
            reloj.tick(int(velocidad * 60))

            if accion_idx >= len(secuencia):
                print(f"Secuencia completada. Altura maxima: {2950 - altura_maxima:.0f}px | Progreso: {progreso}%")
                time.sleep(2)
                ejecutando = False

    pygame.quit()


def cargar_secuencia():
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
    parser.add_argument("--velocidad", type=float, default=0.5)
    parser.add_argument("--repeticiones", type=int, default=1)
    parser.add_argument("--frames", type=int, default=20)
    args = parser.parse_args()

    secuencia = cargar_secuencia()
    if secuencia:
        evaluar_con_render(secuencia, args.frames, args.velocidad, args.repeticiones)
