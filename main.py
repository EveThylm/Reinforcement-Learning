import pygame
import constantes
import sys
from personaje import Personaje
from mapa import crear_mapa

pygame.init()

ventana = pygame.display.set_mode((constantes.ancho_ventana, constantes.alto_ventana))
pygame.display.set_caption("Jumpikingo")

def escalar_img(image,scale):
    w=image.get_width()
    h=image.get_height()
    nueva_imagen=pygame.transform.scale(image,(w*scale,h*scale))
    return nueva_imagen

animaciones=[]
for i in range(7):
    img= pygame.image.load(rf"assets\images\characters\player\Player_{i}.png")
    img= escalar_img(img,constantes.scala_personaje)
    animaciones.append(img)

# Cargar backgrounds
def cargar_bg(ruta, ancho_objetivo):
    img= pygame.image.load(ruta)
    try:
        img= img.convert()
    except:
        img= img.convert_alpha()
    ratio= ancho_objetivo / img.get_width()
    alto_objetivo= int(img.get_height() * ratio)
    return pygame.transform.scale(img, (ancho_objetivo, alto_objetivo))

backgrounds= []
y_acumulado= 0
for i in range(1, 8):
    if i == 2:
        bg= cargar_bg(rf"assets\images\background\background_2.png.jpg", 800)
    else:
        bg= cargar_bg(rf"assets\images\background\background_{i}.png", 800)
    backgrounds.append((bg, y_acumulado))
    y_acumulado += bg.get_height()

mapa = crear_mapa()

nivel_actual= mapa
jugador= Personaje(constantes.spawn_x, constantes.spawn_y, animaciones)

camara_y= 0

mover_izquierda=False
mover_derecha=False

reloj= pygame.time.Clock()

run= True
while run == True:

    reloj.tick(constantes.fps)

    target_camara_y= jugador.forma.centery - constantes.alto_ventana // 2
    camara_y += (target_camara_y - camara_y) * 0.1

    ventana.fill(constantes.color_bg)

    for bg_img, bg_y in backgrounds:
        dibujar_y= bg_y - camara_y
        if dibujar_y + bg_img.get_height() > 0 and dibujar_y < constantes.alto_ventana:
            ventana.blit(bg_img, (0, dibujar_y))

    delta_x=0

    if jugador.on_ground and not jugador.cargando:
        if mover_derecha:
            delta_x= constantes.velocidad
        if mover_izquierda:
            delta_x= -constantes.velocidad

    if not jugador.on_ground:
        delta_x= jugador.velocidad_x

    if jugador.cargando:
        if mover_derecha:
            jugador.set_direccion(1)
        elif mover_izquierda:
            jugador.set_direccion(-1)

    jugador.aplicar_gravedad()
    jugador.forma.y += jugador.velocidad_y

    # Detectar suelo
    jugador.on_ground= False
    pies= pygame.Rect(jugador.forma.x, jugador.forma.bottom, jugador.forma.width, 4)
    for plat in nivel_actual.plataformas:
        if pies.colliderect(plat.rect):
            jugador.on_ground= True
            if jugador.velocidad_y >= 0:
                jugador.forma.bottom= plat.rect.top
                jugador.velocidad_y= 0
            break

    jugador.movimiento(delta_x)

    # Colisiones con plataformas (techo y laterales)
    for plat in nivel_actual.plataformas:
        if jugador.forma.colliderect(plat.rect):
            if jugador.velocidad_y < 0:
                jugador.forma.top= plat.rect.bottom
                jugador.velocidad_y= 0
            elif not jugador.on_ground:
                if delta_x > 0:
                    jugador.forma.right= plat.rect.left
                elif delta_x < 0:
                    jugador.forma.left= plat.rect.right

    # Limites horizontales
    if jugador.forma.left < 0:
        jugador.forma.left= 0
    if jugador.forma.right > constantes.ancho_ventana:
        jugador.forma.right= constantes.ancho_ventana

    # Si cae al fondo del mapa, respawn al inicio
    if jugador.forma.top > constantes.umbral_caida:
        jugador.forma.center= (constantes.spawn_x, constantes.spawn_y)
        jugador.velocidad_y= 0
        jugador.velocidad_x= 0
        jugador.on_ground= True
        camara_y= jugador.forma.centery - constantes.alto_ventana // 2

    jugador.update()

    nivel_actual.dibujar(ventana, camara_y)
    jugador.dibujar(ventana, camara_y)

    # HUD
    font= pygame.font.SysFont(None, 30)
    progreso= max(0, min(100, int((constantes.suelo_y - jugador.forma.centery) / (constantes.suelo_y - 50) * 100)))
    texto_progreso= font.render(f"Progreso: {progreso}%", True, (255, 255, 255))
    ventana.blit(texto_progreso, (10, 10))
    texto_reset= font.render("R: Reiniciar", True, (180, 180, 180))
    ventana.blit(texto_reset, (10, 40))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run= False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                mover_izquierda= True
            if event.key == pygame.K_RIGHT:
                mover_derecha= True
            if event.key == pygame.K_SPACE:
                jugador.empezar_carga()
            if event.key == pygame.K_r:
                jugador.forma.center= (constantes.spawn_x, constantes.spawn_y)
                jugador.velocidad_y= 0
                jugador.velocidad_x= 0
                jugador.on_ground= True
                jugador.cargando= False
                jugador.tiempo_carga= 0
                camara_y= jugador.forma.centery - constantes.alto_ventana // 2

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                mover_izquierda= False
            if event.key == pygame.K_RIGHT:
                mover_derecha= False
            if event.key == pygame.K_SPACE:
                jugador.soltar_salto()

    pygame.display.update()
pygame.quit()
sys.exit()