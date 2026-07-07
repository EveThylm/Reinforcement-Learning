import pygame
from plataforma import Plataforma

class Nivel():
    def __init__(self, plataformas):
        self.plataformas= plataformas

    def dibujar(self, interfaz, camara_y):
        for plat in self.plataformas:
            plat.dibujar(interfaz, camara_y)
