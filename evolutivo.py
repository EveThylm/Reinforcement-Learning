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
        en_aire = False

        debug = getattr(self, '_debug', False)
        
        for accion in secuencia:
            for frame in range(frames_por_accion):
                # Saltos directos (sin carga)
                # 0=idle, 1=izq, 2=der
                if jugador.on_ground:
                    if accion == 1:
                        jugador.velocidad_y = -constantes.fuerza_salto_max
                        jugador.velocidad_x = -8
                        jugador.on_ground = False
                        en_aire = True
                    elif accion == 2:
                        jugador.velocidad_y = -constantes.fuerza_salto_max
                        jugador.velocidad_x = 8
                        jugador.on_ground = False
                        en_aire = True

                # Aplicar gravedad
                jugador.aplicar_gravedad()

                # Guardar posición anterior
                prev_y = jugador.forma.centery
                prev_x = jugador.forma.centerx

                # Mover vertical
                jugador.forma.y += jugador.velocidad_y

                # Colisión vertical
                landed = False
                for plat in self.mapa.plataformas:
                    if jugador.forma.colliderect(plat.rect):
                        if jugador.velocidad_y > 0 and prev_y <= plat.rect.top + 5:
                            # Cayendo y estaba arriba: aterrizar encima
                            jugador.forma.bottom = plat.rect.top
                            jugador.velocidad_y = 0
                            jugador.velocidad_x = 0
                            jugador.on_ground = True
                            en_aire = False
                            landed = True
                        elif jugador.velocidad_y < 0:
                            # Subiendo: chocar contra techo
                            jugador.forma.top = plat.rect.bottom
                            jugador.velocidad_y = 0
                        break
                
                # Si no aterrizó y está cayendo, ya no está en suelo
                if not landed and jugador.velocidad_y > 0:
                    jugador.on_ground = False

                # Mover horizontal
                jugador.forma.x += jugador.velocidad_x

                # Colisión horizontal
                for plat in self.mapa.plataformas:
                    if jugador.forma.colliderect(plat.rect):
                        if not jugador.on_ground:
                            if jugador.velocidad_x > 0:
                                jugador.forma.right = plat.rect.left
                            elif jugador.velocidad_x < 0:
                                jugador.forma.left = plat.rect.right
                        jugador.velocidad_x = 0
                        break

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
                    en_aire = False

                jugador.update()

                # Actualizar tracking
                altura_actual = jugador.forma.centery

                if altura_actual < altura_maxima_aires:
                    altura_maxima_aires = altura_actual

                if jugador.on_ground:
                    pasos_en_suelo += 1
                    if pasos_en_suelo >= 3 and altura_actual < altura_maxima_suelo:
                        altura_maxima_suelo = altura_actual
                else:
                    pasos_en_suelo = 0

        fitness_suelo = 2950 - altura_maxima_suelo
        fitness_aire = 2950 - altura_maxima_aires
        # Premiar más el progreso en aire (el agente necesita estar en el aire para subir)
        fitness = fitness_suelo * 0.7 + fitness_aire * 0.5
        return max(0, fitness), altura_maxima_suelo, altura_maxima_aires


def crear_secuencia_aleatoria(longitud=10):
    return [random.randint(0, 2) for _ in range(longitud)]

def crear_secuencia_inteligente(longitud=10):
    """Secuencia óptima: saltar der → esperar aterrizar → saltar izq → esperar"""
    secuencia = []
    patron = [2, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]
    for i in range(longitud):
        if i < len(patron):
            secuencia.append(patron[i])
        else:
            secuencia.append(0)
    return secuencia


def mutar_secuencia(secuencia, tasa_mutacion=0.2):
    nueva = secuencia.copy()
    for i in range(len(nueva)):
        if random.random() < tasa_mutacion:
            nueva[i] = random.randint(0, 2)
    return nueva

def mutar_por_segmentos(secuencia, tasa_mutacion=0.2, max_segmento=10):
    """Muta segmentos consecutivos de la secuencia"""
    nueva = secuencia.copy()
    i = 0
    while i < len(nueva):
        if random.random() < tasa_mutacion:
            longitud = random.randint(1, min(max_segmento, len(nueva) - i))
            patron = random.randint(0, 2)
            for j in range(i, i + longitud):
                nueva[j] = patron
            i += longitud
        else:
            i += 1
    return nueva


def cruzar_secuencias(padre1, padre2):
    punto = random.randint(1, len(padre1) - 1)
    hijo = padre1[:punto] + padre2[punto:]
    return hijo


def seleccionar_mejores(poblacion, fitnesses, n=5):
    indices = sorted(range(len(fitnesses)), key=lambda i: fitnesses[i], reverse=True)
    return [poblacion[i] for i in indices[:n]]


def ejecutar_evolutivo(
    generaciones=500,
    tamano_poblacion=50,
    longitud_secuencia=1000,
    frames_por_accion=30,
    tasa_mutacion=0.3,
    elites=5,
):
    print("=== Algoritmo Evolutivo - Jump King ===")
    print(f"Generaciones: {generaciones}")
    print(f"Población: {tamano_poblacion}")
    print(f"Acciones por secuencia: {longitud_secuencia}")
    print()

    juego = JuegoEvolutivo()

    poblacion = []
    # Incluir algunas semillas inteligentes
    for _ in range(tamano_poblacion // 3):
        poblacion.append(crear_secuencia_inteligente(longitud_secuencia))
    # Resto aleatorio
    for _ in range(tamano_poblacion - len(poblacion)):
        poblacion.append(crear_secuencia_aleatoria(longitud_secuencia))

    mejor_fitness_global = 0
    mejor_secuencia_global = None
    mejor_altura_global = 2950

    for gen in range(generaciones):
        fitnesses = []
        alturas = []
        for secuencia in poblacion:
            fitness, altura_suelo, _ = juego.evaluar_secuencia(secuencia, frames_por_accion)
            fitnesses.append(fitness)
            alturas.append(altura_suelo)

        mejor_idx = fitnesses.index(max(fitnesses))
        mejor_fitness_gen = fitnesses[mejor_idx]
        mejor_altura_gen = alturas[mejor_idx]
        mejor_secuencia_gen = poblacion[mejor_idx]

        if mejor_fitness_gen > mejor_fitness_global:
            mejor_fitness_global = mejor_fitness_gen
            mejor_secuencia_global = mejor_secuencia_gen.copy()
            mejor_altura_global = mejor_altura_gen
            print(f"Gen {gen+1}: ¡Nuevo mejor! Fitness: {mejor_fitness_global} | Altura: {2950 - mejor_altura_global:.0f}px")
        elif gen % 50 == 0:
            promedio = sum(fitnesses) / len(fitnesses)
            print(f"Gen {gen+1}: Mejor local: {mejor_fitness_gen} | Promedio: {promedio:.1f} | Global: {mejor_fitness_global}")

        mejores = seleccionar_mejores(poblacion, fitnesses, elites)
        nueva_poblacion = mejores.copy()

        while len(nueva_poblacion) < tamano_poblacion:
            if random.random() < 0.5:
                padre = random.choice(mejores)
                if random.random() < 0.5:
                    hijo = mutar_secuencia(padre, tasa_mutacion)
                else:
                    hijo = mutar_por_segmentos(padre, tasa_mutacion)
            else:
                padre1 = random.choice(mejores)
                padre2 = random.choice(mejores)
                hijo = cruzar_secuencias(padre1, padre2)
                hijo = mutar_secuencia(hijo, tasa_mutacion * 0.5)
            nueva_poblacion.append(hijo)

        # Reiniciar 10% de la población si no hay mejora
        if gen > 0 and gen % 20 == 0 and mejor_fitness_gen == mejor_fitness_global:
            n_restart = max(1, tamano_poblacion // 10)
            for i in range(n_restart):
                idx = -(i + 1)
                nueva_poblacion[idx] = crear_secuencia_aleatoria(longitud_secuencia)

        poblacion = nueva_poblacion

    print()
    print("=== RESULTADO FINAL ===")
    print(f"Mejor fitness: {mejor_fitness_global}")
    print(f"Mejor altura (suelo): {2950 - mejor_altura_global:.0f}px")
    print(f"Mejor secuencia: {mejor_secuencia_global}")

    with open("mejor_secuencia.txt", "w") as f:
        f.write(str(mejor_secuencia_global))
    print("Secuencia guardada en: mejor_secuencia.txt")

    return mejor_secuencia_global, mejor_fitness_global


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Algoritmo evolutivo para Jump King")
    parser.add_argument("--generaciones", type=int, default=500)
    parser.add_argument("--poblacion", type=int, default=50)
    parser.add_argument("--acciones", type=int, default=1000)
    parser.add_argument("--mutacion", type=float, default=0.3)
    args = parser.parse_args()

    mejor_secuencia, mejor_fitness = ejecutar_evolutivo(
        generaciones=args.generaciones,
        tamano_poblacion=args.poblacion,
        longitud_secuencia=args.acciones,
        tasa_mutacion=args.mutacion,
    )
