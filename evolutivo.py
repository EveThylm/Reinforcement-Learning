import pygame
import random
import constantes
from personaje import Personaje
from plataforma import Plataforma
from nivel import Nivel


class JuegoEvolutivo:
    def __init__(self):
        pygame.init()
        self.ventana = pygame.Surface((constantes.ancho_ventana, constantes.alto_ventana))
        self.animaciones = []
        for i in range(7):
            img = pygame.image.load(rf"assets\images\characters\player\Player_{i}.png")
            w, h = img.get_width(), img.get_height()
            img = pygame.transform.scale(img, (w * constantes.scala_personaje, h * constantes.scala_personaje))
            self.animaciones.append(img)
        self.mapa = self._crear_mapa()

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

    def evaluar_secuencia(self, secuencia, frames_por_accion=15):
        """Evalúa una secuencia de acciones y retorna el fitness."""
        jugador = Personaje(60, 2930, self.animaciones)
        jugador.on_ground = True

        altura_maxima_suelo = 2950
        pasos_en_suelo = 0
        altura_maxima_aires = 2950
        cargando = False
        tiempo_carga = 0
        direccion = 0
        en_aire = False
        prev_y = jugador.forma.centery
        prev_x = jugador.forma.centerx

        for accion in secuencia:
            # Ejecutar acción durante varios frames
            for frame in range(frames_por_accion):
                # Procesar acción
                if accion == 0:
                    # Idle: soltar carga si hay → saltar
                    if cargando:
                        fuerza = min(tiempo_carga * (constantes.fuerza_salto_max / constantes.tiempo_carga_max), constantes.fuerza_salto_max)
                        jugador.velocidad_y = -fuerza
                        jugador.velocidad_x = direccion * constantes.velocidad
                        jugador.on_ground = False
                        cargando = False
                        tiempo_carga = 0
                        en_aire = True
                elif accion == 1:
                    # Cargar hacia la izquierda
                    if jugador.on_ground and not cargando:
                        cargando = True
                        tiempo_carga = 0
                        direccion = -1
                elif accion == 2:
                    # Cargar hacia la derecha
                    if jugador.on_ground and not cargando:
                        cargando = True
                        tiempo_carga = 0
                        direccion = 1
                elif accion == 3:
                    # Cargar salto aleatorio
                    if jugador.on_ground and not cargando:
                        cargando = True
                        tiempo_carga = 0
                        import random
                        direccion = random.choice([-1, 1])

                # Incrementar carga
                if cargando:
                    tiempo_carga += 1
                    # Saltar automáticamente después de 40 frames
                    if tiempo_carga >= constantes.tiempo_carga_max:
                        fuerza = constantes.fuerza_salto_max
                        jugador.velocidad_y = -fuerza
                        jugador.velocidad_x = direccion * constantes.velocidad
                        jugador.on_ground = False
                        cargando = False
                        tiempo_carga = 0
                        en_aire = True

                # Física
                jugador.aplicar_gravedad()
                jugador.forma.y += jugador.velocidad_y

                # Detectar suelo
                jugador.on_ground = False
                for plat in self.mapa.plataformas:
                    if (prev_y <= plat.rect.top and jugador.forma.bottom >= plat.rect.top and
                        jugador.velocidad_y >= 0 and
                        jugador.forma.right > plat.rect.left and 
                        jugador.forma.left < plat.rect.right):
                        jugador.forma.bottom = plat.rect.top
                        jugador.velocidad_y = 0
                        jugador.velocidad_x = 0
                        jugador.on_ground = True
                        en_aire = False
                        break

                prev_y = jugador.forma.centery

                # Colisiones
                for plat in self.mapa.plataformas:
                    if jugador.forma.colliderect(plat.rect):
                        if jugador.velocidad_y < 0:
                            jugador.forma.top = plat.rect.bottom
                            jugador.velocidad_y = 0
                        elif not jugador.on_ground:
                            if jugador.velocidad_x > 0:
                                jugador.forma.right = plat.rect.left
                            elif jugador.velocidad_x < 0:
                                jugador.forma.left = plat.rect.right

                # Movimiento horizontal (siempre)
                jugador.forma.x += jugador.velocidad_x

                # Límites
                if jugador.forma.left < 0:
                    jugador.forma.left = 0
                if jugador.forma.right > constantes.ancho_ventana:
                    jugador.forma.right = constantes.ancho_ventana

                # Respawn si cae
                if jugador.forma.top > 3100:
                    jugador.forma.center = (60, 2930)
                    jugador.velocidad_y = 0
                    jugador.velocidad_x = 0
                    jugador.on_ground = True
                    cargando = False
                    tiempo_carga = 0
                    en_aire = False

                jugador.update()

                # Actualizar tracking
                altura_actual = jugador.forma.centery

                if altura_actual < altura_maxima_aires:
                    altura_maxima_aires = altura_actual

                # Solo guardar altura si está en suelo
                if jugador.on_ground:
                    pasos_en_suelo += 1
                    if pasos_en_suelo >= 10 and altura_actual < altura_maxima_suelo:
                        altura_maxima_suelo = altura_actual
                else:
                    pasos_en_suelo = 0

        # Fitness: altura alcanzada en suelo (menor = mejor)
        fitness = 2950 - altura_maxima_suelo
        return max(0, fitness), altura_maxima_suelo, altura_maxima_aires


def crear_secuencia_aleatoria(longitud=10):
    """Crea una secuencia aleatoria de acciones."""
    return [random.randint(0, 3) for _ in range(longitud)]


def mutar_secuencia(secuencia, tasa_mutacion=0.2):
    """Muta una secuencia cambiando algunas acciones."""
    nueva = secuencia.copy()
    for i in range(len(nueva)):
        if random.random() < tasa_mutacion:
            nueva[i] = random.randint(0, 3)
    return nueva


def cruzar_secuencias(padre1, padre2):
    """Cruza dos secuencias tomando partes de cada una."""
    punto = random.randint(1, len(padre1) - 1)
    hijo = padre1[:punto] + padre2[punto:]
    return hijo


def seleccionar_mejores(poblacion, fitnesses, n=5):
    """Selecciona las n mejores secuencias."""
    indices = sorted(range(len(fitnesses)), key=lambda i: fitnesses[i], reverse=True)
    return [poblacion[i] for i in indices[:n]]


def ejecutar_evolutivo(
    generaciones=500,
    tamano_poblacion=50,
    longitud_secuencia=1000,
    frames_por_accion=20,
    tasa_mutacion=0.3,
    elites=5,
):
    """Ejecuta el algoritmo evolutivo."""
    print("=== Algoritmo Evolutivo - Jump King ===")
    print(f"Generaciones: {generaciones}")
    print(f"Población: {tamano_poblacion}")
    print(f"Acciones por secuencia: {longitud_secuencia}")
    print()

    juego = JuegoEvolutivo()

    # Crear población inicial
    poblacion = [crear_secuencia_aleatoria(longitud_secuencia) for _ in range(tamano_poblacion)]

    mejor_fitness_global = 0
    mejor_secuencia_global = None
    mejor_altura_global = 2950

    for gen in range(generaciones):
        # Evaluar cada secuencia
        fitnesses = []
        alturas = []
        for secuencia in poblacion:
            fitness, altura_suelo, _ = juego.evaluar_secuencia(secuencia, frames_por_accion)
            fitnesses.append(fitness)
            alturas.append(altura_suelo)

        # Encontrar la mejor de esta generación
        mejor_idx = fitnesses.index(max(fitnesses))
        mejor_fitness_gen = fitnesses[mejor_idx]
        mejor_altura_gen = alturas[mejor_idx]
        mejor_secuencia_gen = poblacion[mejor_idx]

        # Actualizar mejor global
        if mejor_fitness_gen > mejor_fitness_global:
            mejor_fitness_global = mejor_fitness_gen
            mejor_secuencia_global = mejor_secuencia_gen.copy()
            mejor_altura_global = mejor_altura_gen
            print(f"Gen {gen+1}: ¡Nuevo mejor! Fitness: {mejor_fitness_gen} | Altura: {mejor_altura_global:.0f} | Secuencia: {mejor_secuencia_global}")
        elif gen % 50 == 0:
            promedio = sum(fitnesses) / len(fitnesses)
            print(f"Gen {gen+1}: Mejor local: {mejor_fitness_gen} | Promedio: {promedio:.1f} | Global: {mejor_fitness_global}")

        # Seleccionar mejores (elitismo)
        mejores = seleccionar_mejores(poblacion, fitnesses, elites)

        # Crear nueva población
        nueva_poblacion = mejores.copy()

        while len(nueva_poblacion) < tamano_poblacion:
            if random.random() < 0.7:
                # Mutar un elite
                padre = random.choice(mejores)
                hijo = mutar_secuencia(padre, tasa_mutacion)
            else:
                # Cruzar dos elites
                padre1 = random.choice(mejores)
                padre2 = random.choice(mejores)
                hijo = cruzar_secuencias(padre1, padre2)
                hijo = mutar_secuencia(hijo, tasa_mutacion * 0.5)

            nueva_poblacion.append(hijo)

        poblacion = nueva_poblacion

    print()
    print("=== RESULTADO FINAL ===")
    print(f"Mejor fitness: {mejor_fitness_global}")
    print(f"Mejor altura (suelo): {mejor_altura_global:.0f}")
    print(f"Mejor secuencia: {mejor_secuencia_global}")

    # Guardar mejor secuencia
    with open("mejor_secuencia.txt", "w") as f:
        f.write(str(mejor_secuencia_global))
    print("Secuencia guardada en: mejor_secuencia.txt")

    return mejor_secuencia_global, mejor_fitness_global


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Algoritmo evolutivo para Jump King")
    parser.add_argument("--generaciones", type=int, default=500, help="Número de generaciones")
    parser.add_argument("--poblacion", type=int, default=50, help="Tamaño de la población")
    parser.add_argument("--acciones", type=int, default=1000, help="Acciones por secuencia")
    parser.add_argument("--mutacion", type=float, default=0.3, help="Tasa de mutación")
    args = parser.parse_args()

    mejor_secuencia, mejor_fitness = ejecutar_evolutivo(
        generaciones=args.generaciones,
        tamano_poblacion=args.poblacion,
        longitud_secuencia=args.acciones,
        tasa_mutacion=args.mutacion,
    )
