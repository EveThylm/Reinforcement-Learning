from plataforma import Plataforma
from nivel import Nivel


def crear_mapa():
    return Nivel([
        # ===== SUELO =====
        Plataforma(0, 2950, 800, 50),

        # ===== SECCION 1: Inicio amplio =====
        Plataforma(300, 2840, 250, 20),
        Plataforma(50, 2750, 180, 20),
        Plataforma(450, 2750, 180, 20),
        Plataforma(200, 2660, 140, 20),
        Plataforma(500, 2660, 120, 20),
        Plataforma(100, 2570, 150, 20),

        # ===== SECCION 2: Bifurcacion =====
        Plataforma(30, 2480, 130, 20),
        Plataforma(200, 2400, 120, 20),
        Plataforma(450, 2470, 120, 20),
        Plataforma(550, 2380, 130, 20),
        Plataforma(300, 2310, 140, 20),

        # ===== SECCION 3: Descenso lateral =====
        Plataforma(500, 2300, 110, 20),
        Plataforma(620, 2220, 120, 20),
        Plataforma(450, 2150, 110, 20),
        Plataforma(250, 2100, 120, 20),

        # ===== SECCION 4: Subida con plataformas mixtas =====
        Plataforma(400, 2010, 120, 20),
        Plataforma(180, 1930, 130, 20),
        Plataforma(400, 1850, 120, 20),
        Plataforma(180, 1770, 130, 20),
        Plataforma(400, 1690, 120, 20),

        # ===== SECCION 5: Zigzag amplio =====
        Plataforma(180, 1610, 140, 20),
        Plataforma(380, 1530, 140, 20),
        Plataforma(180, 1450, 140, 20),
        Plataforma(380, 1370, 140, 20),

        # ===== SECCION 6: Zigzag =====
        Plataforma(180, 1290, 130, 20),
        Plataforma(380, 1210, 130, 20),
        Plataforma(180, 1130, 130, 20),
        Plataforma(380, 1050, 130, 20),
        Plataforma(180, 970, 130, 20),

        # ===== SECCION 7: Subida final =====
        Plataforma(380, 890, 130, 20),
        Plataforma(180, 810, 130, 20),
        Plataforma(380, 730, 130, 20),

        # ===== SECCION 8: Saltos largos =====
        Plataforma(450, 650, 120, 20),
        Plataforma(200, 570, 120, 20),
        Plataforma(450, 490, 120, 20),
        Plataforma(200, 410, 120, 20),

        # ===== SECCION 9: Precision final =====
        Plataforma(350, 340, 100, 20),
        Plataforma(150, 270, 100, 20),
        Plataforma(400, 200, 100, 20),
        Plataforma(250, 130, 100, 20),

        # ===== CUMBRE =====
        Plataforma(300, 50, 200, 30),
    ])


WAYPOINT_Y_VALUES = [
    2950, 2840, 2750, 2660, 2570, 2480, 2470, 2400, 2380, 2310, 2300,
    2220, 2150, 2100, 2010, 1930, 1850, 1770, 1690, 1610,
    1530, 1450, 1370, 1290, 1210, 1130, 1050, 970,
    890, 810, 730, 650, 570, 490, 410, 340,
    270, 200, 130, 50,
]
