import constantes
from mapa import WAYPOINT_Y_VALUES


def calcular_fitness(altura_maxima_suelo, altura_maxima_aires, waypoints_visitados, altura_actual_suelo):
    fitness_suelo = constantes.suelo_y - altura_maxima_suelo
    fitness_aire = constantes.suelo_y - altura_maxima_aires
    waypoint_bonus = len(waypoints_visitados) * 50
    caida = altura_actual_suelo - altura_maxima_suelo if altura_actual_suelo > altura_maxima_suelo else 0
    fitness = fitness_suelo * 1.0 + fitness_aire * 0.5 + waypoint_bonus - caida * 2
    return max(0, fitness), {
        "suelo": fitness_suelo,
        "suelo_px": constantes.suelo_y - altura_maxima_suelo,
        "aire": fitness_aire,
        "aire_px": constantes.suelo_y - altura_maxima_aires,
        "waypoints": waypoint_bonus,
        "waypoints_count": len(waypoints_visitados),
        "waypoints_total": len(WAYPOINT_Y_VALUES),
        "caida": caida,
        "caida_px": caida,
        "fitness_raw": fitness
    }
