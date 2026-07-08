import pygame
import random
import time
import json
import constantes
from personaje import Personaje
from mapa import crear_mapa, WAYPOINT_Y_VALUES
import multiprocessing
import os


def _evaluar_individual(args):
    secuencia, frames_por_accion, animaciones_data = args
    pygame.init()
    ventana = pygame.Surface((constantes.ancho_ventana, constantes.alto_ventana))
    animaciones = []
    for data in animaciones_data:
        img = pygame.image.frombytes(data[0], data[1], data[2])
        animaciones.append(img)
    mapa = crear_mapa()
    jugador = Personaje(constantes.spawn_x, constantes.spawn_y, animaciones)
    jugador.on_ground = True

    altura_maxima_suelo = constantes.suelo_y
    pasos_en_suelo = 0
    altura_maxima_aires = constantes.suelo_y
    waypoints_visitados = set()
    altura_actual_suelo = constantes.suelo_y

    for accion in secuencia:
        for frame in range(frames_por_accion):
            if jugador.on_ground:
                if accion == 1:
                    jugador.velocidad_y = -constantes.fuerza_salto_max
                    jugador.velocidad_x = -constantes.vx_salto
                    jugador.on_ground = False
                elif accion == 2:
                    jugador.velocidad_y = -constantes.fuerza_salto_max
                    jugador.velocidad_x = constantes.vx_salto
                    jugador.on_ground = False
                elif accion == 3:
                    jugador.velocidad_y = -12
                    jugador.velocidad_x = -constantes.vx_salto
                    jugador.on_ground = False
                elif accion == 4:
                    jugador.velocidad_y = -12
                    jugador.velocidad_x = constantes.vx_salto
                    jugador.on_ground = False

            jugador.aplicar_gravedad()

            jugador.forma.y += jugador.velocidad_y

            jugador.on_ground = False
            pies = pygame.Rect(jugador.forma.x, jugador.forma.bottom, jugador.forma.width, 4)
            for plat in mapa.plataformas:
                if pies.colliderect(plat.rect):
                    jugador.on_ground = True
                    if jugador.velocidad_y >= 0:
                        jugador.forma.bottom = plat.rect.top
                        jugador.velocidad_y = 0
                        jugador.velocidad_x = 0
                    break

            jugador.forma.x += jugador.velocidad_x

            for plat in mapa.plataformas:
                if jugador.forma.colliderect(plat.rect):
                    if jugador.velocidad_y < 0:
                        jugador.forma.top = plat.rect.bottom
                        jugador.velocidad_y = 0
                    elif not jugador.on_ground:
                        if jugador.velocidad_x > 0:
                            jugador.forma.right = plat.rect.left
                        elif jugador.velocidad_x < 0:
                            jugador.forma.left = plat.rect.right

            if jugador.forma.left < 0:
                jugador.forma.left = 0
            if jugador.forma.right > constantes.ancho_ventana:
                jugador.forma.right = constantes.ancho_ventana

            if jugador.forma.top > constantes.umbral_caida:
                jugador.forma.center = (constantes.spawn_x, constantes.spawn_y)
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
                    altura_actual_suelo = altura_actual
                else:
                    altura_actual_suelo = altura_actual
            else:
                pasos_en_suelo = 0

            for i, wp_y in enumerate(WAYPOINT_Y_VALUES):
                if altura_actual <= wp_y + 10 and jugador.on_ground:
                    waypoints_visitados.add(i)

    fitness_suelo = constantes.suelo_y - altura_maxima_suelo
    fitness_aire = constantes.suelo_y - altura_maxima_aires
    waypoint_bonus = len(waypoints_visitados) * 50
    caida = altura_actual_suelo - altura_maxima_suelo if altura_actual_suelo > altura_maxima_suelo else 0
    fitness = fitness_suelo * 1.0 + fitness_aire * 0.5 + waypoint_bonus - caida * 2
    return max(0, fitness), altura_maxima_suelo, altura_maxima_aires


class JuegoEvolutivo:
    def __init__(self):
        pygame.init()
        self.ventana = pygame.Surface((constantes.ancho_ventana, constantes.alto_ventana))
        self.animaciones = []
        self.animaciones_data = []
        for i in range(7):
            img = pygame.image.load(rf"assets\images\characters\player\Player_{i}.png")
            w, h = img.get_width(), img.get_height()
            img = pygame.transform.scale(img, (w * constantes.scala_personaje, h * constantes.scala_personaje))
            self.animaciones.append(img)
            self.animaciones_data.append((
                pygame.image.tobytes(img, "RGBA"),
                img.get_size(),
                "RGBA"
            ))
        self.mapa = crear_mapa()

    def evaluar_secuencia(self, secuencia, frames_por_accion=30):
        jugador = Personaje(constantes.spawn_x, constantes.spawn_y, self.animaciones)
        jugador.on_ground = True

        altura_maxima_suelo = constantes.suelo_y
        pasos_en_suelo = 0
        altura_maxima_aires = constantes.suelo_y
        waypoints_visitados = set()
        altura_actual_suelo = constantes.suelo_y

        for accion in secuencia:
            for frame in range(frames_por_accion):
                if jugador.on_ground:
                    if accion == 1:
                        jugador.velocidad_y = -constantes.fuerza_salto_max
                        jugador.velocidad_x = -constantes.vx_salto
                        jugador.on_ground = False
                    elif accion == 2:
                        jugador.velocidad_y = -constantes.fuerza_salto_max
                        jugador.velocidad_x = constantes.vx_salto
                        jugador.on_ground = False
                    elif accion == 3:
                        jugador.velocidad_y = -12
                        jugador.velocidad_x = -constantes.vx_salto
                        jugador.on_ground = False
                    elif accion == 4:
                        jugador.velocidad_y = -12
                        jugador.velocidad_x = constantes.vx_salto
                        jugador.on_ground = False

                jugador.aplicar_gravedad()

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

                jugador.forma.x += jugador.velocidad_x

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

                if jugador.forma.left < 0:
                    jugador.forma.left = 0
                if jugador.forma.right > constantes.ancho_ventana:
                    jugador.forma.right = constantes.ancho_ventana

                if jugador.forma.top > constantes.umbral_caida:
                    jugador.forma.center = (constantes.spawn_x, constantes.spawn_y)
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
                        altura_actual_suelo = altura_actual
                    else:
                        altura_actual_suelo = altura_actual
                else:
                    pasos_en_suelo = 0

                for i, wp_y in enumerate(WAYPOINT_Y_VALUES):
                    if altura_actual <= wp_y + 10 and jugador.on_ground:
                        waypoints_visitados.add(i)

        fitness_suelo = constantes.suelo_y - altura_maxima_suelo
        fitness_aire = constantes.suelo_y - altura_maxima_aires
        waypoint_bonus = len(waypoints_visitados) * 50
        caida = altura_actual_suelo - altura_maxima_suelo if altura_actual_suelo > altura_maxima_suelo else 0
        fitness = fitness_suelo * 1.0 + fitness_aire * 0.5 + waypoint_bonus - caida * 2
        return max(0, fitness), altura_maxima_suelo, altura_maxima_aires


def crear_secuencia_aleatoria(longitud=10):
    return [random.randint(0, 4) for _ in range(longitud)]

def crear_secuencia_inteligente(longitud=10):
    secuencia = []
    patron = [2, 0, 0, 0, 0, 4, 0, 0, 0, 0, 1, 0, 0, 0, 0, 3, 0, 0, 0, 0]
    for i in range(longitud):
        if i < len(patron):
            secuencia.append(patron[i])
        else:
            secuencia.append(0)
    return secuencia

def crear_secuencia_espiral(longitud=10):
    secuencia = []
    patron = [2, 0, 0, 4, 0, 0, 1, 0, 0, 3, 0, 0]
    for i in range(longitud):
        if i < len(patron):
            secuencia.append(patron[i])
        else:
            secuencia.append(0)
    return secuencia

def crear_secuencia_pasos(longitud=10):
    secuencia = []
    for i in range(longitud):
        if i % 6 < 2:
            secuencia.append(2)
        elif i % 6 < 4:
            secuencia.append(0)
        else:
            secuencia.append(4)
    return secuencia


def mutar_secuencia(secuencia, tasa_mutacion=0.2):
    nueva = secuencia.copy()
    for i in range(len(nueva)):
        if random.random() < tasa_mutacion:
            nueva[i] = random.randint(0, 4)
    return nueva

def mutar_por_segmentos(secuencia, tasa_mutacion=0.2, max_segmento=10):
    nueva = secuencia.copy()
    i = 0
    while i < len(nueva):
        if random.random() < tasa_mutacion:
            longitud = random.randint(1, min(max_segmento, len(nueva) - i))
            patron = random.randint(0, 4)
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


def seleccionar_por_torneo(poblacion, fitnesses, k=3, n=5):
    ganadores = []
    indices = list(range(len(poblacion)))
    for _ in range(n):
        candidatos = random.sample(indices, min(k, len(indices)))
        mejor_candidato = max(candidatos, key=lambda i: fitnesses[i])
        ganadores.append(poblacion[mejor_candidato])
    return ganadores


def ejecutar_evolutivo(
    generaciones=1000,
    tamano_poblacion=100,
    longitud_secuencia=500,
    frames_por_accion=30,
    tasa_mutacion=0.3,
    elites=5,
    usar_paralelo=False,
):
    print("=" * 60)
    print("     ALGORITMO EVOLUTIVO - JUMP KING")
    print("=" * 60)
    print(f"  Generaciones:        {generaciones}")
    print(f"  Tamaño población:    {tamano_poblacion}")
    print(f"  Acciones/secuencia:  {longitud_secuencia}")
    print(f"  Frames/acción:       {frames_por_accion}")
    print(f"  Tasa mutación:       {tasa_mutacion} (adaptativa)")
    print(f"  Élites:              {elites}")
    print(f"  Selección:           torneo (k=3)")
    print(f"  Paralelo:            {usar_paralelo}")
    print("=" * 60)
    print()

    juego = JuegoEvolutivo()

    poblacion = []
    semillas = [
        crear_secuencia_inteligente,
        crear_secuencia_espiral,
        crear_secuencia_pasos,
    ]
    for i in range(tamano_poblacion):
        if i < len(semillas) * 2:
            funcion = semillas[i % len(semillas)]
            poblacion.append(funcion(longitud_secuencia))
        else:
            poblacion.append(crear_secuencia_aleatoria(longitud_secuencia))

    mejor_fitness_global = 0
    mejor_secuencia_global = None
    mejor_altura_global = constantes.suelo_y
    tiempo_inicio = time.time()
    generaciones_sin_mejora = 0
    tasa_mutacion_actual = tasa_mutacion

    for gen in range(generaciones):
        if usar_paralelo and tamano_poblacion > 5:
            args_list = [
                (sec, frames_por_accion, juego.animaciones_data)
                for sec in poblacion
            ]
            with multiprocessing.Pool(processes=min(os.cpu_count(), tamano_poblacion)) as pool:
                resultados = pool.map(_evaluar_individual, args_list)
            fitnesses = [r[0] for r in resultados]
            alturas = [r[1] for r in resultados]
        else:
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
            generaciones_sin_mejora = 0
            tasa_mutacion_actual = tasa_mutacion * 0.9
            progreso = (constantes.suelo_y - mejor_altura_global) / (constantes.suelo_y - 50) * 100
            print(f"\n{'='*60}")
            print(f"  GEN {gen+1}/{generaciones} - ¡NUEVO MEJOR!")
            print(f"{'='*60}")
            print(f"  Fitness:        {mejor_fitness_global:.1f}")
            print(f"  Altura suelo:   {constantes.suelo_y - mejor_altura_global:.0f}px (Y={mejor_altura_global:.0f})")
            print(f"  Progreso:       {progreso:.1f}%")
            print(f"  Mutación:       {tasa_mutacion_actual:.3f}")
            print(f"  Población:      Mejor={mejor_fitness_gen:.1f} | Peor={peor:.1f} | Prom={promedio:.1f} | Desv={desviacion:.1f}")
            print(f"  Tiempo:         {tiempo_transcurrido:.1f}s transcurridos | ~{tiempo_restante:.1f}s restantes")
            print(f"{'='*60}\n")
        else:
            generaciones_sin_mejora += 1
            if generaciones_sin_mejora > 10:
                tasa_mutacion_actual = min(tasa_mutacion * 2.0, tasa_mutacion_actual * 1.1)
            if gen % 10 == 0:
                progreso = (constantes.suelo_y - mejor_altura_global) / (constantes.suelo_y - 50) * 100
                print(f"\n  GEN {gen+1}/{generaciones}")
                print(f"  Fitness global: {mejor_fitness_global:.1f} | Local: {mejor_fitness_gen:.1f}")
                print(f"  Población:      Mejor={mejor_fitness_gen:.1f} | Peor={peor:.1f} | Prom={promedio:.1f} | Desv={desviacion:.1f}")
                print(f"  Progreso:       {progreso:.1f}% | Altura: {constantes.suelo_y - mejor_altura_global:.0f}px")
                print(f"  Mutación:       {tasa_mutacion_actual:.3f} | Sin mejora: {generaciones_sin_mejora} gens")
                print(f"  Tiempo:         {tiempo_transcurrido:.1f}s | ~{tiempo_restante:.1f}s restantes")
                print()

        elitesSeleccionadas = seleccionar_por_torneo(poblacion, fitnesses, k=3, n=elites)
        nueva_poblacion = elitesSeleccionadas.copy()

        while len(nueva_poblacion) < tamano_poblacion:
            if random.random() < 0.5:
                padre = random.choice(elitesSeleccionadas)
                if random.random() < 0.5:
                    hijo = mutar_secuencia(padre, tasa_mutacion_actual)
                else:
                    hijo = mutar_por_segmentos(padre, tasa_mutacion_actual)
            else:
                padre1 = random.choice(elitesSeleccionadas)
                padre2 = random.choice(elitesSeleccionadas)
                hijo = cruzar_secuencias(padre1, padre2)
                hijo = mutar_secuencia(hijo, tasa_mutacion_actual * 0.5)
            nueva_poblacion.append(hijo)

        if generaciones_sin_mejora > 0 and generaciones_sin_mejora % 20 == 0:
            n_restart = max(1, tamano_poblacion // 10)
            for i in range(n_restart):
                idx = -(i + 1)
                nueva_poblacion[idx] = crear_secuencia_aleatoria(longitud_secuencia)

        poblacion = nueva_poblacion

    tiempo_total = time.time() - tiempo_inicio
    progreso_final = (constantes.suelo_y - mejor_altura_global) / (constantes.suelo_y - 50) * 100

    print()
    print("=" * 60)
    print("     RESULTADO FINAL")
    print("=" * 60)
    print(f"  Mejor fitness:      {mejor_fitness_global:.1f}")
    print(f"  Mejor altura:       {constantes.suelo_y - mejor_altura_global:.0f}px (Y={mejor_altura_global:.0f})")
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
    parser.add_argument("--generaciones", type=int, default=1000)
    parser.add_argument("--poblacion", type=int, default=100)
    parser.add_argument("--acciones", type=int, default=500)
    parser.add_argument("--mutacion", type=float, default=0.3)
    parser.add_argument("--paralelo", action="store_true", help="Usar evaluación paralela")
    args = parser.parse_args()

    mejor_secuencia, mejor_fitness = ejecutar_evolutivo(
        generaciones=args.generaciones,
        tamano_poblacion=args.poblacion,
        longitud_secuencia=args.acciones,
        tasa_mutacion=args.mutacion,
        usar_paralelo=args.paralelo,
    )
