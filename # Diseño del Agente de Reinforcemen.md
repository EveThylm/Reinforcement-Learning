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

# Conclusión

El agente no aprenderá observando imágenes del juego, sino mediante un **vector de características numéricas** cuidadosamente diseñado. Este vector resume el estado del jugador y del entorno en cada instante, proporcionando la información necesaria para que el algoritmo PPO pueda aprender una política de control eficiente.

El uso de observaciones numéricas reduce significativamente el tiempo de entrenamiento, simplifica el diseño del entorno y permite centrar el proyecto en los principios fundamentales del Reinforcement Learning.