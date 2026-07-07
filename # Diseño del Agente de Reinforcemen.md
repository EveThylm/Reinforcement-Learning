# Diseño del Agente de Reinforcement Learning

## Objetivo

El objetivo es entrenar un agente capaz de completar los niveles del juego de forma autónoma utilizando **Reinforcement Learning (RL)**. Para ello, el agente no observará imágenes de la pantalla, sino que recibirá una representación numérica del estado del juego en cada instante.

Este enfoque permite un entrenamiento más rápido, requiere menos recursos computacionales y facilita el análisis del proceso de aprendizaje.

---

# ¿Qué es una observación?

Una **observación** (Observation o State) es toda la información que el agente recibe del entorno antes de tomar una decisión.

En cada paso del entrenamiento ocurre el siguiente ciclo:

```text
Estado actual
      │
      ▼
Observación
      │
      ▼
Red neuronal (PPO)
      │
      ▼
Acción
      │
      ▼
Juego
      │
      ▼
Nuevo estado
      │
      ▼
Nueva observación
```

El agente nunca "ve" el código del juego.

Únicamente recibe un conjunto de valores numéricos que describen el estado actual del mundo.

---

# ¿Por qué utilizar información numérica?

Existen dos formas comunes de representar el estado de un videojuego para Reinforcement Learning.

## Opción 1: Información numérica (State Vector)

El agente recibe únicamente los datos importantes del juego.

Ejemplo:

```text
Posición X = 315
Posición Y = 420

Velocidad X = 3.2
Velocidad Y = -7.5

En el suelo = Sí

Carga del salto = 0.62
```

### Ventajas

- Entrenamiento mucho más rápido.
- Requiere menos memoria.
- Consume menos recursos de GPU.
- Facilita la interpretación del comportamiento del agente.
- Ideal para proyectos académicos y de aprendizaje.

### Desventajas

- El desarrollador debe decidir qué información proporcionar.
- El agente no puede descubrir información que no esté incluida en las observaciones.

---

# Decisión del proyecto

Para este proyecto se utilizará una representación basada en **información numérica**.

Esta decisión se toma porque el objetivo principal es comprender el funcionamiento del algoritmo PPO y del proceso de Reinforcement Learning, sin añadir la complejidad del procesamiento de imágenes.

---

# Diseño de las observaciones

Cada observación será un vector de números que describe el estado actual del jugador y del entorno.

Conceptualmente, cada observación tendrá la siguiente estructura:

```text
[
    posición_x,
    posición_y,
    velocidad_x,
    velocidad_y,
    estado_en_suelo,
    carga_del_salto,
    dirección,
    ...
]
```

Cada elemento representa una característica del estado actual del juego.

---

# Información del jugador

## 1. Posición horizontal (X)

Indica la posición del jugador sobre el eje horizontal.

Permite que el agente conozca su ubicación dentro del nivel.

Ejemplo:

```text
X = 412
```

---

## 2. Posición vertical (Y)

Indica la altura del jugador.

Es probablemente la variable más importante del problema, ya que el objetivo consiste en alcanzar la parte superior del nivel.

Ejemplo:

```text
Y = 128
```

---

## 3. Velocidad horizontal

Representa la velocidad con la que el jugador se mueve hacia la izquierda o hacia la derecha.

Ejemplo:

```text
-5
```

o

```text
3
```

Valores negativos indican movimiento hacia la izquierda.

Valores positivos indican movimiento hacia la derecha.

---

## 4. Velocidad vertical

Indica si el jugador está:

- cayendo
- subiendo
- completamente detenido

Ejemplo:

```text
-12
```

Un valor negativo puede representar un salto.

Un valor positivo puede representar una caída.

---

## 5. Estado "En el suelo"

Variable booleana.

Permite saber si el personaje está apoyado sobre una plataforma.

Valores posibles:

```text
0 = No

1 = Sí
```

Esta información resulta fundamental para decidir cuándo iniciar un salto.

---

## 6. Carga del salto

Jump King basa gran parte de su jugabilidad en la carga del salto.

Esta variable indica qué porcentaje de carga posee el salto actual.

Ejemplo:

```text
0.00
```

No está cargando.

```text
0.50
```

Carga media.

```text
1.00
```

Carga máxima.

---

## 7. Dirección del personaje

Indica hacia dónde está mirando el personaje.

Puede codificarse como:

```text
0 = Izquierda

1 = Derecha
```

Es importante porque la dirección modifica el movimiento horizontal del salto.

---

# Información del entorno

Además del estado del jugador, es conveniente proporcionar información simplificada del entorno.

No se pretende describir todo el mapa, sino únicamente los elementos más relevantes para tomar decisiones.

---

## 8. Distancia al suelo

Indica la distancia entre el jugador y la plataforma inmediatamente inferior.

Permite estimar cuánto falta para aterrizar.

---

## 9. Distancia al techo

Indica la distancia entre el jugador y el obstáculo superior más cercano.

Esta información ayuda a evitar saltos que terminen golpeando un techo.

---

## 10. Distancia a la pared izquierda

Representa la distancia hasta el obstáculo lateral izquierdo más cercano.

Puede utilizarse para decidir cuándo impulsarse desde una pared o evitar colisiones.

---

## 11. Distancia a la pared derecha

Representa la distancia hasta el obstáculo lateral derecho más cercano.

Complementa la información de navegación horizontal.

---

## 12. Altura máxima alcanzada

Registra la mayor altura conseguida durante el episodio actual.

Esta variable permite al agente conocer su progreso dentro del nivel.

---

## 13. Distancia hasta la meta

Indica cuánto falta para llegar al objetivo final del nivel.

Puede calcularse mediante la diferencia de altura o utilizando una distancia geométrica si la meta no está alineada verticalmente.

---

# Ejemplo de observación

```text
[
    420,      // posición X
    185,      // posición Y
    2.5,      // velocidad X
    -6.3,     // velocidad Y
    1,        // en el suelo
    0.72,     // carga del salto
    1,        // mirando derecha
    35,       // distancia al suelo
    48,       // distancia al techo
    12,       // pared izquierda
    80,       // pared derecha
    610,      // altura máxima
    390       // distancia a la meta
]
```

Cada vez que el agente de PPO solicite una acción, recibirá un vector similar a este como entrada para su red neuronal.

---

# Normalización de las observaciones

Es recomendable normalizar los valores antes de entregarlos al agente.

Por ejemplo:

| Variable | Rango original | Rango normalizado |
|-----------|----------------|-------------------|
| Posición X | 0 - 1280 | 0.0 - 1.0 |
| Posición Y | 0 - 720 | 0.0 - 1.0 |
| Velocidad X | -10 - 10 | -1.0 - 1.0 |
| Velocidad Y | -20 - 20 | -1.0 - 1.0 |
| Carga del salto | 0 - 100 | 0.0 - 1.0 |

La normalización mejora la estabilidad y la velocidad del entrenamiento.

---

# Resumen de observaciones

| Observación | Descripción |
|--------------|-------------|
| Posición X | Ubicación horizontal del jugador. |
| Posición Y | Altura actual del jugador. |
| Velocidad X | Movimiento horizontal. |
| Velocidad Y | Movimiento vertical. |
| En el suelo | Indica si puede iniciar un salto. |
| Carga del salto | Nivel de carga acumulado antes de saltar. |
| Dirección | Sentido hacia el que mira el personaje. |
| Distancia al suelo | Distancia hasta la plataforma inferior. |
| Distancia al techo | Distancia hasta el obstáculo superior. |
| Distancia pared izquierda | Distancia al obstáculo lateral izquierdo. |
| Distancia pared derecha | Distancia al obstáculo lateral derecho. |
| Altura máxima | Mayor altura alcanzada durante el episodio. |
| Distancia a la meta | Progreso restante para completar el nivel. |

---

# Espacio de Acciones

El agente interactúa con el juego mediante un conjunto finito de acciones. Dado que Jump King no permite control aéreo, todas las decisiones relevantes ocurren cuando el jugador está en el suelo.

## Acciones Discretas (5 acciones)

| ID | Acción | Descripción |
|----|--------|-------------|
| 0 | **Idle** | No realizar ninguna acción. El personaje permanece inactivo. |
| 1 | **Mover izquierda** | Caminar hacia la izquierda (válido solo en suelo). |
| 2 | **Mover derecha** | Caminar hacia la derecha (válido solo en suelo). |
| 3 | **Cargar salto** | Iniciar o mantener la carga del salto. |
| 4 | **Liberar salto** | Ejecutar el salto con la carga acumulada. |

### Por qué un espacio discreto

- El juego solo permite control en el suelo (caminar, cargar, soltar).
- En el aire no hay acciones disponibles: la velocidad queda fija al lanzar el salto.
- Un espacio `Discrete(5)` es sencillo de implementar con PPO y librerías como Stable Baselines3.

### Flujo de decisiones del agente

```text
¿Está en el suelo?
    │
    ├─ Sí → ¿Está cargando?
    │         ├─ Sí → Puede: Liberar salto (4) o mantener carga (3)
    │         └─ No → Puede: Idle (0), Mover izq (1), Mover der (2), Cargar (3)
    │
    └─ No → El agente no actúa (espera a aterrizar)
```

---

# Función de Recompensa

La función de recompensa define qué comportamientos se desea fomentar o penalizar. Un buen diseño de recompensas es esencial para que el agente aprenda a escalar el nivel de forma eficiente.

## Recompensas por evento

| Evento | Recompensa | Justificación |
|--------|------------|---------------|
| Ganar altura (+1 px) | **+1.0** | Fomenta progreso hacia la cumbre. |
| Perder altura (-1 px) | **-1.5** | Penalización mayor para desalentar caídas. |
| Ejecutar salto | **+0.5** | Incentiva al agente a saltar. |
| Alcanzar nueva plataforma | **+5.0** | Recompensa por explorar y avanzar. |
| Alcanzar la cumbre (meta) | **+1000.0** | Recompensa grande por completar el nivel. |
| Caer al inicio del nivel | **-500.0** | Penalización fuerte por retroceso severo. |
| Cada paso de tiempo | **-0.1** | Incentiva completar el nivel rápidamente. |
| Inactividad (>30 pasos) | **-0.2** | Penalización por quedarse quieto mucho tiempo. |

## Diseño de la recompensa

La recompensa se calcula en cada paso del `step()` del entorno:

```text
recompensa = 0

recompensa += (altura_actual - altura_anterior) * 1.0      # ganar altura
recompensa += (altura_actual - altura_anterior) * -1.5     # perder altura (penalización extra)
recompensa -= 0.1                                          # costo por paso

if accion == 4:                                            # ejecutar salto
    recompensa += 0.5

if plataforma_nueva:                                       # nueva plataforma visitada
    recompensa += 5.0

if altura_actual <= altura_meta:                           # completar nivel
    recompensa += 1000.0

if altura_actual > 3100:                                   # caer al inicio
    recompensa -= 500.0

if en_suelo and sin_cargar and pasos_inactivos > 30:       # inactividad prolongada
    recompensa -= 0.2
```

## Consideraciones

- **Equilibrio entre recompensa y penalización:** La penalización por perder altura (1.5) es mayor que la recompensa por ganarla (1.0) para que el agente aprenda a evitar caídas en lugar de simplemente subir y caer repetidamente.
- **Recompensa terminal grande (+1000):** Garantiza que el agente priorice llegar a la meta como objetivo final.
- **Penalización por tiempo (-0.1/paso):** Evita que el agente se quede estancado o dé vueltas sin progresar.

---

# Resumen del Diseño

| Componente | Descripción |
|------------|-------------|
| **Observaciones** | Vector de 13 valores numéricos normalizados (posición, velocidad, entorno). |
| **Acciones** | 5 acciones discretas (idle, mover izq, mover der, cargar salto, liberar salto). |
| **Recompensas** | Ganar altura (+1), perder altura (-1.5), saltar (+0.5), nueva plataforma (+5), meta (+1000), caer (-500), tiempo (-0.1), inactividad (-0.2). |
| **Algoritmo** | PPO (Proximal Policy Optimization). |

---

# Conclusión

El agente no aprenderá observando imágenes del juego, sino mediante un **vector de características numéricas** cuidadosamente diseñado. Este vector resume el estado del jugador y del entorno en cada instante, proporcionando la información necesaria para que el algoritmo PPO pueda aprender una política de control eficiente.

El uso de observaciones numéricas reduce significativamente el tiempo de entrenamiento, simplifica el diseño del entorno y permite centrar el proyecto en los principios fundamentales del Reinforcement Learning.