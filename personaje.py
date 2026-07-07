import pygame
import constantes

class Personaje():
    def __init__(self, x, y, animaciones):
        self.flip = False
        self.animaciones = animaciones
        self.frame_index= 0
        self.update_time= pygame.time.get_ticks()
        self.image= animaciones[self.frame_index]
        self.forma= pygame.Rect(0, 0, constantes.ancho_personaje, constantes.alto_personaje)
        self.forma.center= (x, y)

        # Física
        self.velocidad_x= 0
        self.velocidad_y= 0
        self.on_ground= False

        # Salto cargado
        self.cargando= False
        self.tiempo_carga= 0
        self.direccion= 0  # -1 izquierda, 0 sin dirección, 1 derecha

    def movimiento(self, delta_x):
        if delta_x < 0:
            self.flip= True
        if delta_x > 0:
            self.flip= False
        self.forma.x += delta_x

    def empezar_carga(self):
        if self.on_ground:
            self.cargando= True
            self.tiempo_carga= 0

    def set_direccion(self, dir):
        self.direccion= dir
        if dir < 0:
            self.flip= True
        elif dir > 0:
            self.flip= False

    def soltar_salto(self):
        if self.cargando and self.on_ground:
            fuerza= min(self.tiempo_carga * (constantes.fuerza_salto_max / constantes.tiempo_carga_max), constantes.fuerza_salto_max)
            self.velocidad_y= -fuerza
            self.velocidad_x= self.direccion * constantes.velocidad
            self.on_ground= False
        self.cargando= False
        self.tiempo_carga= 0
        self.direccion= 0

    def aplicar_gravedad(self):
        if not self.on_ground:
            self.velocidad_y += constantes.gravedad
            if self.velocidad_y > constantes.velocidad_max_caida:
                self.velocidad_y= constantes.velocidad_max_caida
        else:
            self.velocidad_y= 0
            self.velocidad_x= 0

    def update(self):
        if self.cargando:
            self.tiempo_carga += 1

        cooldown_animacion= 100
        self.image= self.animaciones[self.frame_index]
        if pygame.time.get_ticks() - self.update_time >= cooldown_animacion:
            self.frame_index += 1
            self.update_time= pygame.time.get_ticks()
        if self.frame_index >= len(self.animaciones):
            self.frame_index= 0

    def dibujar(self, interfaz, camara_y= 0):
        imagen_flip= pygame.transform.flip(self.image, self.flip, False)
        dibujar_x= self.forma.centerx - imagen_flip.get_width() // 2
        dibujar_y= self.forma.centery - imagen_flip.get_height() // 2 - camara_y
        interfaz.blit(imagen_flip, (dibujar_x, dibujar_y))

        # Barra de carga del salto
        if self.cargando:
            barra_ancho= 40
            barra_alto= 5
            carga_ratio= min(self.tiempo_carga / constantes.tiempo_carga_max, 1.0)
            barra_x= self.forma.centerx - barra_ancho // 2
            barra_y= dibujar_y - 10
            pygame.draw.rect(interfaz, (80, 80, 80), (barra_x, barra_y, barra_ancho, barra_alto))
            pygame.draw.rect(interfaz, (255, 50, 50), (barra_x, barra_y, int(barra_ancho * carga_ratio), barra_alto))
    