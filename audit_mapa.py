import math

FUERZA_SALTO_MAX = 16
GRAVEDAD = 0.5
VX = 8
ANCHO_PERSONAJE = 20

ALTURA_MAX = FUERZA_SALTO_MAX ** 2 / (2 * GRAVEDAD)
TIEMPO_SUBIDA = FUERZA_SALTO_MAX / GRAVEDAD
TIEMPO_TOTAL = TIEMPO_SUBIDA * 2
DISTANCIA_MAX_HORIZONTAL = TIEMPO_TOTAL * VX

PLATAFORMAS = [
    (0, 2950, 800, 50),
    (300, 2840, 250, 20),
    (50, 2750, 180, 20),
    (450, 2750, 180, 20),
    (200, 2660, 140, 20),
    (500, 2660, 120, 20),
    (100, 2570, 150, 20),
    (30, 2480, 130, 20),
    (200, 2400, 120, 20),
    (450, 2470, 120, 20),
    (550, 2380, 130, 20),
    (300, 2310, 140, 20),
    (500, 2300, 110, 20),
    (620, 2220, 120, 20),
    (450, 2150, 110, 20),
    (250, 2100, 120, 20),
    (400, 2010, 120, 20),
    (180, 1930, 130, 20),
    (400, 1850, 120, 20),
    (180, 1770, 130, 20),
    (400, 1690, 120, 20),
    (180, 1610, 140, 20),
    (380, 1530, 140, 20),
    (180, 1450, 140, 20),
    (380, 1370, 140, 20),
    (180, 1290, 130, 20),
    (380, 1210, 130, 20),
    (180, 1130, 130, 20),
    (380, 1050, 130, 20),
    (180, 970, 130, 20),
    (380, 890, 130, 20),
    (180, 810, 130, 20),
    (380, 730, 130, 20),
    (450, 650, 120, 20),
    (200, 570, 120, 20),
    (450, 490, 120, 20),
    (200, 410, 120, 20),
    (350, 340, 100, 20),
    (150, 270, 100, 20),
    (400, 200, 100, 20),
    (250, 130, 100, 20),
    (300, 50, 200, 30),
]


def calcular_saltos_posibles():
    print("=" * 70)
    print("  AUDITORIA DE SALTOS - JUMP KING")
    print("=" * 70)
    print(f"  Altura max salto:    {ALTURA_MAX:.0f}px")
    print(f"  Distancia max horiz: {DISTANCIA_MAX_HORIZONTAL:.0f}px")
    print(f"  Tiempo aire:         {TIEMPO_TOTAL:.0f} frames")
    print("=" * 70)
    print()

    alcanzables = set()
    alcanzables.add(0)

    for origen_idx, (ox, oy, ow, oh) in enumerate(PLATAFORMAS):
        centro_origen_x = ox + ow / 2
        centro_origen_y = oy

        destinos_desde_origen = []

        for destino_idx, (dx, dy, dw, dh) in enumerate(PLATAFORMAS):
            if destino_idx == origen_idx:
                continue

            delta_y = centro_origen_y - dy

            if delta_y <= 0:
                continue

            if delta_y > ALTURA_MAX:
                continue

            min_dist_x = max(0, (dx + dw) - (ox + ow))
            max_dist_x = max(0, (ox + ow) - dx) + (dx + dw - dx)

            if min_dist_x <= DISTANCIA_MAX_HORIZONTAL:
                reachable = True
                dificultad = "FACIL" if delta_y < ALTURA_MAX * 0.5 else "MEDIA"
                if min_dist_x > DISTANCIA_MAX_HORIZONTAL * 0.7:
                    dificultad = "DIFICIL"
                destinos_desde_origen.append((destino_idx, dy, dx, dw, delta_y, min_dist_x, dificultad))
                alcanzables.add(destino_idx)

        if destinos_desde_origen:
            destinos_desde_origen.sort(key=lambda d: d[3])
            print(f"  Plataforma {origen_idx:2d} (Y={oy:4d}, X={ox:3d}-{ox+ow:3d}):")
            for didx, dy, dx, dw, dy_jump, dx_min, diff in destinos_desde_origen[:5]:
                print(f"    -> Plat {didx:2d} (Y={dy:4d}, X={dx:3d}-{dx+dw:3d}) | "
                      f"dY={dy_jump:3.0f}px dX_min={dx_min:3.0f}px | {diff}")
            print()

    no_alcanzables = set(range(len(PLATAFORMAS))) - alcanzables
    if no_alcanzables:
        print("  PLATAFORMAS INALCANZABLES desde abajo:")
        for idx in sorted(no_alcanzables):
            x, y, w, h = PLATAFORMAS[idx]
            print(f"    Plat {idx:2d}: Y={y}, X={x}-{x+w}")
    else:
        print("  Todas las plataformas son alcanzables desde al menos una debajo.")

    print()
    print("=" * 70)
    print("  ANALISIS DE SECCIONES CRITICAS")
    print("=" * 70)

    criticas = []
    for i in range(len(PLATAFORMAS) - 1):
        ox, oy, ow, oh = PLATAFORMAS[i]
        dx, dy, dw, dh = PLATAFORMAS[i + 1]
        delta_y = oy - dy
        delta_x_min = max(0, (dx + dw) - (ox + ow))

        if delta_y > ALTURA_MAX * 0.8 or delta_x_min > DISTANCIA_MAX_HORIZONTAL * 0.6:
            criticas.append((i, i + 1, delta_y, delta_x_min))

    if criticas:
        print("  Saltos dificiles entre plataformas consecutivas:")
        for orig, dest, dy, dx in criticas:
            ox, oy, ow, oh = PLATAFORMAS[orig]
            dx_pos, dy_pos, dw, dh = PLATAFORMAS[dest]
            print(f"    Plat {orig} -> Plat {dest}: dY={dy:.0f}px dX={dx:.0f}px")
    else:
        print("  No hay saltos criticos entre plataformas consecutivas.")


if __name__ == "__main__":
    calcular_saltos_posibles()
