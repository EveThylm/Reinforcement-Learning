import pygame
import random
import time
import json
import constantes
from personaje import Personaje
from mapa import crear_mapa, WAYPOINT_Y_VALUES


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
        self.mapa = crear_mapa()

    def evaluar_secuencia(self, secuencia, frames_por_accion=30):
        jugador = Personaje(60, 2930, self.animaciones)
        jugador.on_ground = True

        altura_maxima_suelo = 2950
        pasos_en_suelo = 0
        altura_maxima_aires = 2950
        waypoints_visitados = set()

        for accion in secuencia:
            for frame in range(frames_por_accion):
                if jugador.on_ground:
                    if accion == 1:
                        jugador.velocidad_y = -constantes.fuerza_salto_max
                        jugador.velocidad_x = -8
                        jugador.on_ground = False
                    elif accion == 2:
                        jugador.velocidad_y = -constantes.fuerza_salto_max
                        jugador.velocidad_x = 8
                        jugador.on_ground = False

                jugador.aplicar_gravedad()

                prev_y = jugador.forma.centery
                jugador.forma.y += jugador.velocidad_y

                jugador.on_ground = False
                pies = pygame.Rect(jugador.forma.x, jugador.forma.bottom, jugador.forma.width, 4)
                for plat in self.mapa.plataformas:
                    if pies.colliderect(plat.rect):
                        jugador.on_ground = True
                        if jugador.velocidad_y >= 0:
                            jugador.forma.bottom = plat.rect.top
                            jugador.velocidad_y = 0
                            jugador.velocidad_x = 0
                        break

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

                jugador.forma.x += jugador.velocidad_x

                if jugador.forma.left < 0:
                    jugador.forma.left = 0
                if jugador.forma.right > constantes.ancho_ventana:
                    jugador.forma.right = constantes.ancho_ventana

                if jugador.forma.top > 3100:
                    jugador.forma.center = (60, 2930)
                    jugador.velocidad_y = 0
                    jugador.velocidad_x = 0
                    jugador.on_ground = True

                jugador.update()

                altura_actual = jugador.forma.centery

                if altura_actual < altura_maxima_aires:
                    altura_maxima_aires = altura_actual

                if jugador.on_ground:
                    pasos_en_suelo += 1
                    if pasos_en_suelo >= 3 and altura_actual < altura_maxima_suelo:
                        altura_maxima_suelo = altura_actual
                else:
                    pasos_en_suelo = 0

                for i, wp_y in enumerate(WAYPOINT_Y_VALUES):
                    if altura_actual <= wp_y + 10 and jugador.on_ground:
                        waypoints_visitados.add(i)

        fitness_suelo = 2950 - altura_maxima_suelo
        fitness_aire = 2950 - altura_maxima_aires
        waypoint_bonus = len(waypoints_visitados) * 100
        fitness = fitness_suelo * 0.7 + fitness_aire * 0.3 + waypoint_bonus
        return max(0, fitness), altura_maxima_suelo, altura_maxima_aires


def crear_secuencia_aleatoria(longitud=10):
    return [random.randint(0, 2) for _ in range(longitud)]

def crear_secuencia_inteligente(longitud=10):
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
    print("=" * 60)
    print("     ALGORITMO EVOLUTIVO - JUMP KING")
    print("=" * 60)
    print(f"  Generaciones:        {generaciones}")
    print(f"  Tamaño población:    {tamano_poblacion}")
    print(f"  Acciones/secuencia:  {longitud_secuencia}")
    print(f"  Frames/acción:       {frames_por_accion}")
    print(f"  Tasa mutación:       {tasa_mutacion}")
    print(f"  Élites:              {elites}")
    print(f"  Fitness:            waypoint-based (bonificación por plataforma)")
    print("=" * 60)
    print()

    juego = JuegoEvolutivo()

    poblacion = []
    for _ in range(tamano_poblacion // 3):
        poblacion.append(crear_secuencia_inteligente(longitud_secuencia))
    for _ in range(tamano_poblacion - len(poblacion)):
        poblacion.append(crear_secuencia_aleatoria(longitud_secuencia))

    mejor_fitness_global = 0
    mejor_secuencia_global = None
    mejor_altura_global = 2950
    tiempo_inicio = time.time()

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

        promedio = sum(fitnesses) / len(fitnesses)
        peor = min(fitnesses)
        varianza = sum((f - promedio) ** 2 for f in fitnesses) / len(fitnesses)
        desviacion = varianza ** 0.5

        tiempo_transcurrido = time.time() - tiempo_inicio
        tiempo_por_gen = tiempo_transcurrido / (gen + 1)
        tiempo_restante = tiempo_por_gen * (generaciones - gen - 1)

        if mejor_fitness_gen > mejor_fitness_global:
            mejor_fitness_global = mejor_fitness_gen
            mejor_secuencia_global = mejor_secuencia_gen.copy()
            mejor_altura_global = mejor_altura_gen
            progreso = (2950 - mejor_altura_global) / 2900 * 100
            print(f"\n{'='*60}")
            print(f"  GEN {gen+1}/{generaciones} - ¡NUEVO MEJOR!")
            print(f"{'='*60}")
            print(f"  Fitness:        {mejor_fitness_global:.1f}")
            print(f"  Altura suelo:   {2950 - mejor_altura_global:.0f}px (Y={mejor_altura_global:.0f})")
            print(f"  Progreso:       {progreso:.1f}%")
            print(f"  Población:      Mejor={mejor_fitness_gen:.1f} | Peor={peor:.1f} | Prom={promedio:.1f} | Desv={desviacion:.1f}")
            print(f"  Tiempo:         {tiempo_transcurrido:.1f}s transcurridos | ~{tiempo_restante:.1f}s restantes")
            print(f"{'='*60}\n")
        elif gen % 10 == 0:
            progreso = (2950 - mejor_altura_global) / 2900 * 100
            print(f"\n  GEN {gen+1}/{generaciones}")
            print(f"  Fitness global: {mejor_fitness_global:.1f} | Local: {mejor_fitness_gen:.1f}")
            print(f"  Población:      Mejor={mejor_fitness_gen:.1f} | Peor={peor:.1f} | Prom={promedio:.1f} | Desv={desviacion:.1f}")
            print(f"  Progreso:       {progreso:.1f}% | Altura: {2950 - mejor_altura_global:.0f}px")
            print(f"  Tiempo:         {tiempo_transcurrido:.1f}s | ~{tiempo_restante:.1f}s restantes")
            print()

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

        if gen > 0 and gen % 20 == 0 and mejor_fitness_gen == mejor_fitness_global:
            n_restart = max(1, tamano_poblacion // 10)
            for i in range(n_restart):
                idx = -(i + 1)
                nueva_poblacion[idx] = crear_secuencia_aleatoria(longitud_secuencia)

        poblacion = nueva_poblacion

    tiempo_total = time.time() - tiempo_inicio
    progreso_final = (2950 - mejor_altura_global) / 2900 * 100

    print()
    print("=" * 60)
    print("     RESULTADO FINAL")
    print("=" * 60)
    print(f"  Mejor fitness:      {mejor_fitness_global:.1f}")
    print(f"  Mejor altura:       {2950 - mejor_altura_global:.0f}px (Y={mejor_altura_global:.0f})")
    print(f"  Progreso:           {progreso_final:.1f}%")
    print(f"  Tiempo total:       {tiempo_total:.1f} segundos")
    print(f"  Generaciones:       {generaciones}")
    print("=" * 60)

    with open("mejor_secuencia.txt", "w") as f:
        json.dump(mejor_secuencia_global, f)
    print(f"\n  Secuencia guardada en: mejor_secuencia.txt")
    print(f"  Longitud secuencia: {len(mejor_secuencia_global)} acciones")

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
