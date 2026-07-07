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

        # Inicializar Pygame
        pygame.init()
        if render_mode == "human":
            self.ventana = pygame.display.set_mode(
                (constantes.ancho_ventana, constantes.alto_ventana)
            )
            pygame.display.set_caption("Jump King RL - Entrenamiento")
        else:
            self.ventana = pygame.Surface(
                (constantes.ancho_ventana, constantes.alto_ventana)
            )

        self.reloj = pygame.time.Clock()

        # Cargar animaciones
        self.animaciones = []
        for i in range(7):
            img = pygame.image.load(
                rf"assets\images\characters\player\Player_{i}.png"
            )
            w = img.get_width()
            h = img.get_height()
            escala = constantes.scala_personaje
            img = pygame.transform.scale(img, (w * escala, h * escala))
            self.animaciones.append(img)

        # Crear mapa
        self.mapa = self._crear_mapa()

        # Espacios de observación y acción
        self.observation_space = spaces.Box(
            low=-1.0, high=1.0, shape=(13,), dtype=np.float32
        )
        self.action_space = spaces.Discrete(5)

        # Estado del juego
        self.jugador = None
        self.camara_y = 0
        self.altura_maxima = 0
        self.altura_inicial = 2950
        self.meta_y = 50
        self.pasos = 0
        self.altura_minima_episodio = 2950
        self._pasos_inactivo = 0

        # Historial de acciones
        self.historial_acciones = {
            "idle": 0,
            "left": 0,
            "right": 0,
            "charge_jump": 0,
            "jump": 0,
        }

        # Plataformas visitadas
        self.plataformas_visitadas = set()
        self._ultima_plataforma = None

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
        self.jugador = Personaje(50, 2930, self.animaciones)
        self.camara_y = 0
        self.altura_maxima = 0
        self.altura_minima_episodio = 2950
        self.pasos = 0
        self._accion_anterior = None
        self._pasos_inactivo = 0

        # Reset historial de acciones
        self.historial_acciones = {
            "idle": 0,
            "left": 0,
            "right": 0,
            "charge_jump": 0,
            "jump": 0,
        }

        # Reset plataformas visitadas
        self.plataformas_visitadas = set()
        self._ultima_plataforma = None

        return self._obtener_observacion(), {}

    def _obtener_observacion(self):
        j = self.jugador
        obs = np.zeros(13, dtype=np.float32)

        # Posición normalizada
        obs[0] = j.forma.centerx / constantes.ancho_ventana
        obs[1] = j.forma.centery / constantes.alto_ventana

        # Velocidad normalizada
        obs[2] = j.velocidad_x / 10.0
        obs[3] = j.velocidad_y / 20.0

        # Estado
        obs[4] = 1.0 if j.on_ground else 0.0
        obs[5] = min(j.tiempo_carga / constantes.tiempo_carga_max, 1.0)

        # Dirección
        if j.direccion < 0:
            obs[6] = 0.0
        elif j.direccion > 0:
            obs[6] = 1.0
        else:
            obs[6] = 0.5

        # Distancias a obstáculos
        obs[7] = self._distancia_suelo() / 200.0
        obs[8] = self._distancia_techo() / 200.0
        obs[9] = self._distancia_pared_izq() / 200.0
        obs[10] = self._distancia_pared_der() / 200.0

        # Progreso
        obs[11] = self.altura_maxima / constantes.alto_ventana
        obs[12] = (j.forma.centery - self.meta_y) / (
            self.altura_inicial - self.meta_y
        )

        return np.clip(obs, -1.0, 1.0)

    def _distancia_suelo(self):
        j = self.jugador
        pies_y = j.forma.bottom
        min_dist = 300.0
        for plat in self.mapa.plataformas:
            if plat.rect.top >= pies_y:
                dist = plat.rect.top - pies_y
                if dist < min_dist:
                    min_dist = dist
        return min_dist

    def _distancia_techo(self):
        j = self.jugador
        tope_y = j.forma.top
        min_dist = 300.0
        for plat in self.mapa.plataformas:
            if plat.rect.bottom <= tope_y:
                dist = tope_y - plat.rect.bottom
                if dist < min_dist:
                    min_dist = dist
        return min_dist

    def _distancia_pared_izq(self):
        j = self.jugador
        izq_x = j.forma.left
        min_dist = 200.0
        for plat in self.mapa.plataformas:
            if plat.rect.right <= izq_x:
                dist = izq_x - plat.rect.right
                if dist < min_dist:
                    min_dist = dist
        return min_dist

    def _distancia_pared_der(self):
        j = self.jugador
        der_x = j.forma.right
        min_dist = 200.0
        for plat in self.mapa.plataformas:
            if plat.rect.left >= der_x:
                dist = plat.rect.left - der_x
                if dist < min_dist:
                    min_dist = dist
        return min_dist

    def step(self, action):
        self.pasos += 1
        altura_anterior = self.jugador.forma.centery

        # Registrar acción en historial
        if action == 0:
            self.historial_acciones["idle"] += 1
        elif action == 1:
            self.historial_acciones["left"] += 1
        elif action == 2:
            self.historial_acciones["right"] += 1
        elif action == 3:
            self.historial_acciones["charge_jump"] += 1
        elif action == 4:
            self.historial_acciones["jump"] += 1

        # Ejecutar acción
        self._ejecutar_accion(action)

        # Física del juego
        self._actualizar_fisica()

        # Verificar si está en una nueva plataforma
        plataforma_actual = self._obtener_plataforma_actual()
        recompensa_nueva_plat = 0
        if plataforma_actual is not None:
            if plataforma_actual not in self.plataformas_visitadas:
                self.plataformas_visitadas.add(plataforma_actual)
                recompensa_nueva_plat = 5.0  # Recompensa por nueva plataforma
            self._ultima_plataforma = plataforma_actual

        # Calcular recompensa
        recompensa = self._calcular_recompensa(altura_anterior) + recompensa_nueva_plat

        # Actualizar tracking
        altura_actual = self.jugador.forma.centery
        if altura_actual < self.altura_maxima:
            self.altura_maxima = altura_actual
        if altura_actual < self.altura_minima_episodio:
            self.altura_minima_episodio = altura_actual

        # Verificar fin del episodio (meta arriba, Y=50)
        terminado = altura_actual <= self.meta_y

        # Límite de pasos (truncated)
        truncado = self.pasos >= 5000

        self._accion_anterior = action

        if self.render_mode == "human":
            self._renderizar()

        return (
            self._obtener_observacion(),
            recompensa,
            terminado,
            truncado,
            {
                "altura": altura_actual,
                "altura_maxima": self.altura_maxima,
                "pasos": self.pasos,
                "progreso": max(
                    0,
                    min(
                        100,
                        int(
                            (self.altura_inicial - altura_actual)
                            / (self.altura_inicial - self.meta_y)
                            * 100
                        ),
                    ),
                ),
                "action_idle": self.historial_acciones["idle"],
                "action_left": self.historial_acciones["left"],
                "action_right": self.historial_acciones["right"],
                "action_charge_jump": self.historial_acciones["charge_jump"],
                "action_jump": self.historial_acciones["jump"],
                "plataformas_visitadas": len(self.plataformas_visitadas),
                "nueva_plataforma": recompensa_nueva_plat > 0,
            },
        )

    def _ejecutar_accion(self, action):
        j = self.jugador
        delta_x = 0

        # Acción 4: Liberar salto (solo si está cargando)
        if action == 4:
            if j.cargando:
                # Si no tiene dirección, asignar aleatoria
                if j.direccion == 0:
                    j.set_direccion(random.choice([-1, 1]))
                j.soltar_salto()

        # Acción 3: Cargar salto (mantener mientras se envíe)
        elif action == 3:
            if j.on_ground and not j.cargando:
                j.empezar_carga()
            # Si ya está cargando, simplemente continúa (no hace nada extra)

        # Acción 1: Mover izquierda
        elif action == 1:
            if j.cargando:
                # Cambiar dirección mientras carga
                j.set_direccion(-1)
            elif j.on_ground:
                delta_x = -constantes.velocidad

        # Acción 2: Mover derecha
        elif action == 2:
            if j.cargando:
                # Cambiar dirección mientras carga
                j.set_direccion(1)
            elif j.on_ground:
                delta_x = constantes.velocidad

        # Acción 0: Idle
        else:
            pass

        # En el aire, mantener velocidad horizontal
        if not j.on_ground:
            delta_x = j.velocidad_x

        j.aplicar_gravedad()
        j.forma.y += j.velocidad_y

        j.on_ground = False
        pies = pygame.Rect(
            j.forma.x, j.forma.bottom, j.forma.width, 4
        )
        for plat in self.mapa.plataformas:
            if pies.colliderect(plat.rect):
                j.on_ground = True
                if j.velocidad_y >= 0:
                    j.forma.bottom = plat.rect.top
                    j.velocidad_y = 0
                break

        for plat in self.mapa.plataformas:
            if j.forma.colliderect(plat.rect):
                if j.velocidad_y < 0:
                    j.forma.top = plat.rect.bottom
                    j.velocidad_y = 0
                elif not j.on_ground:
                    if delta_x > 0:
                        j.forma.right = plat.rect.left
                    elif delta_x < 0:
                        j.forma.left = plat.rect.right

        j.movimiento(delta_x)

        if j.forma.left < 0:
            j.forma.left = 0
        if j.forma.right > constantes.ancho_ventana:
            j.forma.right = constantes.ancho_ventana

        if j.forma.top > 3100:
            j.forma.center = (50, 2930)
            j.velocidad_y = 0
            j.velocidad_x = 0
            j.on_ground = True
            j.cargando = False
            j.tiempo_carga = 0
            self.camara_y = j.forma.centery - constantes.alto_ventana // 2

        j.update()

    def _actualizar_fisica(self):
        target = self.jugador.forma.centery - constantes.alto_ventana // 2
        self.camara_y += (target - self.camara_y) * 0.1

    def _obtener_plataforma_actual(self):
        """Retorna el índice de la plataforma en la que está parado el jugador."""
        j = self.jugador
        pies = pygame.Rect(j.forma.x, j.forma.bottom, j.forma.width, 4)
        for i, plat in enumerate(self.mapa.plataformas):
            if pies.colliderect(plat.rect):
                return i
        return None

    def _calcular_recompensa(self, altura_anterior):
        altura_actual = self.jugador.forma.centery
        recompensa = 0

        # Ganar altura (valores menores = más arriba)
        delta_altura = altura_anterior - altura_actual
        if delta_altura > 0:
            recompensa += delta_altura * 1.0
        else:
            recompensa += delta_altura * -1.5

        # Recompensa por ejecutar un salto (acción 4)
        if self._accion_anterior == 4:
            recompensa += 0.5

        # Costo por paso
        recompensa -= 0.1

        # Penalización por inactividad (en suelo sin cargar por mucho tiempo)
        if self.jugador.on_ground and not self.jugador.cargando:
            self._pasos_inactivo += 1
            if self._pasos_inactivo > 30:
                recompensa -= 0.2
        else:
            self._pasos_inactivo = 0

        # Meta alcanzada (Y=50 es la cumbre, arriba)
        if altura_actual <= self.meta_y:
            recompensa += 1000.0

        # Caer al inicio
        if altura_actual > 3100:
            recompensa -= 500.0

        return recompensa

    def _renderizar(self):
        self.ventana.fill(constantes.color_bg)
        self.mapa.dibujar(self.ventana, self.camara_y)
        self.jugador.dibujar(self.ventana, self.camara_y)

        font = pygame.font.SysFont(None, 30)
        progreso = max(
            0,
            min(
                100,
                int(
                    (2950 - self.jugador.forma.centery) / (2950 - 50) * 100
                ),
            ),
        )
        texto = font.render(f"Progreso: {progreso}% | Pasos: {self.pasos}", True, (255, 255, 255))
        self.ventana.blit(texto, (10, 10))

        pygame.display.update()

    def render(self):
        if self.render_mode == "rgb_array":
            return np.transpose(
                pygame.surfarray.array3d(self.ventana), (1, 0, 2)
            )

    def close(self):
        pygame.quit()
