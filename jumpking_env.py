import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pygame
import random
import constantes
from personaje import Personaje
from plataforma import Plataforma
from nivel import Nivel


class JumpKingEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 60}

    def __init__(self, render_mode=None):
        super().__init__()
        self.render_mode = render_mode

        pygame.init()
        if render_mode == "human":
            self.ventana = pygame.display.set_mode(
                (constantes.ancho_ventana, constantes.alto_ventana)
            )
            pygame.display.set_caption("Jump King RL")
        else:
            self.ventana = pygame.Surface(
                (constantes.ancho_ventana, constantes.alto_ventana)
            )

        self.animaciones = []
        for i in range(7):
            img = pygame.image.load(rf"assets\images\characters\player\Player_{i}.png")
            w, h = img.get_width(), img.get_height()
            img = pygame.transform.scale(img, (w * constantes.scala_personaje, h * constantes.scala_personaje))
            self.animaciones.append(img)

        self.mapa = self._crear_mapa()

        self.observation_space = spaces.Box(low=-1.0, high=1.0, shape=(10,), dtype=np.float32)
        self.action_space = spaces.Discrete(3)

        self.jugador = None
        self.camara_y = 0
        self.altura_inicial = 2950
        self.meta_y = 50
        self.pasos = 0
        self._altura_maxima = 2950
        self.plataformas_visitadas = set()

    def _crear_mapa(self):
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

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.jugador = Personaje(60, 2930, self.animaciones)
        self.jugador.on_ground = True
        self.camara_y = 0
        self.pasos = 0
        self._altura_maxima = 2950
        self.plataformas_visitadas = set()
        return self._obtener_observacion(), {}

    def _obtener_observacion(self):
        j = self.jugador
        obs = np.zeros(10, dtype=np.float32)
        obs[0] = j.forma.centery / constantes.alto_ventana
        obs[1] = j.forma.centerx / constantes.ancho_ventana
        obs[2] = j.velocidad_y / 20.0
        obs[3] = j.velocidad_x / 10.0
        obs[4] = 1.0 if j.on_ground else 0.0

        mejor_dist = float('inf')
        mejor_x = 0
        mejor_y = 0
        for plat in self.mapa.plataformas:
            if plat.rect.bottom < j.forma.centery:
                dx = plat.rect.centerx - j.forma.centerx
                dy = j.forma.centery - plat.rect.centery
                dist = abs(dx) + abs(dy)
                if dist < mejor_dist:
                    mejor_dist = dist
                    mejor_x = dx
                    mejor_y = dy
        obs[5] = mejor_x / constantes.ancho_ventana
        obs[6] = mejor_y / constantes.alto_ventana

        izq_x = -1.0
        izq_y = 0.0
        for plat in self.mapa.plataformas:
            if plat.rect.right < j.forma.left and abs(plat.rect.centery - j.forma.centery) < 200:
                izq_x = (j.forma.centerx - plat.rect.centerx) / constantes.ancho_ventana
                izq_y = (j.forma.centery - plat.rect.centery) / constantes.alto_ventana
                break
        obs[7] = izq_x

        der_x = -1.0
        der_y = 0.0
        for plat in self.mapa.plataformas:
            if plat.rect.left > j.forma.right and abs(plat.rect.centery - j.forma.centery) < 200:
                der_x = (plat.rect.centerx - j.forma.centerx) / constantes.ancho_ventana
                der_y = (j.forma.centery - plat.rect.centery) / constantes.alto_ventana
                break
        obs[8] = der_x

        obs[9] = (j.forma.centery - self.meta_y) / (self.altura_inicial - self.meta_y)
        return np.clip(obs, -1.0, 1.0)

    def step(self, action):
        self.pasos += 1
        altura_anterior = self.jugador.forma.centery
        action = int(action)

        # Saltos directos (sin carga)
        if self.jugador.on_ground:
            if action == 1:
                self.jugador.velocidad_y = -constantes.fuerza_salto_max
                self.jugador.velocidad_x = -8
                self.jugador.on_ground = False
            elif action == 2:
                self.jugador.velocidad_y = -constantes.fuerza_salto_max
                self.jugador.velocidad_x = 8
                self.jugador.on_ground = False

        # Fisica
        self.jugador.aplicar_gravedad()
        prev_y = self.jugador.forma.centery
        self.jugador.forma.y += self.jugador.velocidad_y

        # Colision vertical
        landed = False
        for plat in self.mapa.plataformas:
            if self.jugador.forma.colliderect(plat.rect):
                if self.jugador.velocidad_y > 0 and prev_y <= plat.rect.top + 5:
                    self.jugador.forma.bottom = plat.rect.top
                    self.jugador.velocidad_y = 0
                    self.jugador.velocidad_x = 0
                    self.jugador.on_ground = True
                    landed = True
                elif self.jugador.velocidad_y < 0:
                    self.jugador.forma.top = plat.rect.bottom
                    self.jugador.velocidad_y = 0
                break
        
        if not landed and self.jugador.velocidad_y > 0:
            self.jugador.on_ground = False

        # Movimiento horizontal
        self.jugador.forma.x += self.jugador.velocidad_x

        # Colision horizontal
        for plat in self.mapa.plataformas:
            if self.jugador.forma.colliderect(plat.rect):
                if not self.jugador.on_ground:
                    if self.jugador.velocidad_x > 0:
                        self.jugador.forma.right = plat.rect.left
                    elif self.jugador.velocidad_x < 0:
                        self.jugador.forma.left = plat.rect.right
                self.jugador.velocidad_x = 0
                break

        # Limites
        if self.jugador.forma.left < 0:
            self.jugador.forma.left = 0
        if self.jugador.forma.right > constantes.ancho_ventana:
            self.jugador.forma.right = constantes.ancho_ventana

        # Respawn
        if self.jugador.forma.top > 3100:
            self.jugador.forma.center = (60, 2930)
            self.jugador.velocidad_y = 0
            self.jugador.velocidad_x = 0
            self.jugador.on_ground = True

        self.jugador.update()

        # Camara
        target = self.jugador.forma.centery - constantes.alto_ventana // 2
        self.camara_y += (target - self.camara_y) * 0.1

        # Recompensa
        altura_actual = self.jugador.forma.centery
        recompensa = (altura_anterior - altura_actual) * 0.5

        plat_actual = self._obtener_plataforma_actual()
        if plat_actual is not None and plat_actual not in self.plataformas_visitadas:
            self.plataformas_visitadas.add(plat_actual)
            recompensa += 100.0

        if altura_actual < self._altura_maxima:
            self._altura_maxima = altura_actual
            recompensa += 10.0

        if self.jugador.on_ground and altura_actual == altura_anterior:
            recompensa -= 0.5

        terminado = altura_actual <= self.meta_y
        if terminado:
            recompensa += 2000.0

        if altura_actual > 3100:
            recompensa -= 200.0

        truncado = self.pasos >= 200

        if self.render_mode == "human":
            self._renderizar()

        return (
            self._obtener_observacion(),
            recompensa,
            terminado,
            truncado,
            {
                "altura": altura_actual,
                "progreso": max(0, min(100, int((self.altura_inicial - altura_actual) / (self.altura_inicial - self.meta_y) * 100))),
                "plataformas_visitadas": len(self.plataformas_visitadas),
                "altura_maxima": self._altura_maxima,
            },
        )

    def _obtener_plataforma_actual(self):
        j = self.jugador
        for i, plat in enumerate(self.mapa.plataformas):
            if j.forma.colliderect(plat.rect) and j.on_ground:
                return i
        return None

    def _renderizar(self):
        self.ventana.fill(constantes.color_bg)
        self.mapa.dibujar(self.ventana, self.camara_y)
        self.jugador.dibujar(self.ventana, self.camara_y)

        font = pygame.font.SysFont(None, 30)
        progreso = max(0, min(100, int((2950 - self.jugador.forma.centery) / (2950 - 50) * 100)))
        texto = font.render(f"Progreso: {progreso}% | Plataformas: {len(self.plataformas_visitadas)}", True, (255, 255, 255))
        self.ventana.blit(texto, (10, 10))
        pygame.display.update()

    def render(self):
        if self.render_mode == "rgb_array":
            return np.transpose(pygame.surfarray.array3d(self.ventana), (1, 0, 2))

    def close(self):
        pygame.quit()
