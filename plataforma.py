import pygame
import math

class Plataforma():
    def __init__(self, x, y, ancho, alto):
        self.rect= pygame.Rect(x, y, ancho, alto)
        self.es_inclinada= False

    def dibujar(self, interfaz, camara_y= 0):
        rect_dibujar= self.rect.copy()
        rect_dibujar.y -= camara_y
        pygame.draw.rect(interfaz, (100, 200, 100), rect_dibujar)


class PlataformaInclinada():
    def __init__(self, x, y, ancho, alto, direccion= 1, fuerza_deslizamiento= 3):
        self.rect= pygame.Rect(x, y, ancho, alto)
        self.direccion= direccion  # 1 = desliza a la derecha, -1 = a la izquierda
        self.fuerza_deslizamiento= fuerza_deslizamiento
        self.es_inclinada= True

    def calcular_y(self, x_jugador):
        rel_x= (x_jugador - self.rect.left) / self.rect.width
        rel_x= max(0, min(1, rel_x))
        if self.direccion > 0:
            return self.rect.top + rel_x * self.rect.height
        else:
            return self.rect.top + (1 - rel_x) * self.rect.height

    def dibujar(self, interfaz, camara_y= 0):
        puntos= []
        if self.direccion > 0:
            puntos= [
                (self.rect.left, self.rect.top),
                (self.rect.right, self.rect.bottom),
                (self.rect.left, self.rect.bottom),
            ]
        else:
            puntos= [
                (self.rect.right, self.rect.top),
                (self.rect.left, self.rect.bottom),
                (self.rect.right, self.rect.bottom),
            ]
        puntos_dibujar= [(p[0], p[1] - camara_y) for p in puntos]
        pygame.draw.polygon(interfaz, (200, 150, 50), puntos_dibujar)
        pygame.draw.polygon(interfaz, (160, 120, 40), puntos_dibujar, 2)
