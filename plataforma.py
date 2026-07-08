import pygame


class Plataforma():
    def __init__(self, x, y, ancho, alto):
        self.rect= pygame.Rect(x, y, ancho, alto)
        self.es_inclinada= False

    def dibujar(self, interfaz, camara_y= 0):
        rect_dibujar= self.rect.copy()
        rect_dibujar.y -= camara_y
        pygame.draw.rect(interfaz, (100, 200, 100), rect_dibujar)
