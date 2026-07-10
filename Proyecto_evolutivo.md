# Proyecto Evolutivo - Jump King

## Tabla de Contenidos

1. [Introducción](#1-introducción)
2. [Componentes del Algoritmo](#2-componentes-del-algoritmo)
3. [Flujo Completo del Algoritmo](#3-flujo-completo-del-algoritmo)
4. [Librerías Utilizadas](#4-librerías-utilizadas)
5. [Análisis de Complejidad](#5-análisis-de-complejidad)
6. [Ventajas y Desventajas](#6-ventajas-y-desventajas)
7. [Código Relevante](#7-código-relevante)
8. [Conclusiones](#8-conclusiones)

---

## 1. Introducción

### 1.1 Descripción del Proyecto

Este proyecto implementa un **algoritmo evolutivo** (algoritmo genético) para resolver el juego **Jump King**, un juego de plataformas donde el personaje debe escalar verticalmente saltando entre plataformas.

El objetivo es encontrar una **secuencia óptima de acciones** que permita al personaje llegar lo más alto posible en el mapa del juego.

### 1.2 Objetivo del Algoritmo

```
OBJETIVO: Encontrar una secuencia de acciones [a₁, a₂, ..., aₙ]
          donde cada aᵢ ∈ {0, 1, 2, 3, 4}
          que maximice la altura alcanzada por el personaje.
```

### 1.3 Representación del Problema

| Acción | Significado | Velocidad Y | Velocidad X |
|--------|-------------|-------------|-------------|
| `0` | Idle (no hacer nada) | - | - |
| `1` | Salto alto izquierda | `-fuerza_salto_max` | `-vx_salto` |
| `2` | Salto alto derecha | `-fuerza_salto_max` | `+vx_salto` |
| `3` | Salto bajo izquierda | `-12` | `-vx_salto` |
| `4` | Salto bajo derecha | `-12` | `+vx_salto` |

**Ejemplo de cromosoma:**
```
Secuencia: [2, 0, 0, 4, 0, 0, 1, 0, 0, 3, 2, 0, 0, 4, ...]
            ↑     ↑     ↑     ↑     ↑     ↑     ↑     ↑
           Salto  Idle  Salto  Idle  Salto  Idle  Salto  Idle
           alt.D        alt.I        alt.D        alt.I
```

---

## 2. Componentes del Algoritmo

### 2.1 Representación (Cromosomas)

#### ¿Qué es?

Cada **individuo** (cromosoma) es una secuencia de acciones que representa una estrategia completa para jugar el juego.

#### Estructura del Cromosoma

```python
# Tipo de dato: Lista de enteros
# Longitud típica: 750 acciones
# Valores posibles: {0, 1, 2, 3, 4}

cromosoma = [2, 0, 0, 4, 0, 0, 1, 0, 0, 3, ...]  # 750 elementos
```

#### ¿Por qué es importante?

| Sin representación clara | Con representación clara |
|--------------------------|--------------------------|
| No se puede Evolucionar | Permite operaciones genéticas |
| No hay estructura | Facilita la evaluación |
| No hay herencia | Permite cruce y mutación |

---

### 2.2 Población Inicial

#### ¿Qué es?

El conjunto inicial de individuos que comenzarán a evolucionar.

#### Estrategia de Inicialización

No todos los individuos son aleatorios. Se usan **semillas inteligentes** para dar una base de partida:

```python
# evolutivo.py:381-391
semillas = [
    crear_secuencia_inteligente,  # Patrón predefinido óptimo
    crear_secuencia_espiral,       # Movimiento en espiral
    crear_secuencia_pasos,         # Patrón de pasos rítmicos
]

# Los primeros 6 individuos usan estas semillas
# El resto (94 de 100) son aleatorios
```

#### Ejemplo de Semillas

```python
# Patrón inteligente (evolutivo.py:284-292)
patron = [2, 0, 0, 0, 0, 4, 0, 0, 0, 0, 1, 0, 0, 0, 0, 3, 0, 0, 0, 0]
#          ↑           ↑           ↑           ↑
#         Salto.D     Salto.I     Salto.D     Salto.I
#         (repetir patrón)

# Patrón espiral (evolutivo.py:294-302)
patron = [2, 0, 0, 4, 0, 0, 1, 0, 0, 3, 0, 0]
#          ↑     ↑     ↑     ↑
#         D→I   I→D   I→D   D→I (movimiento circular)

# Individuo aleatorio (evolutivo.py:281-282)
def crear_secuencia_aleatoria(longitud=10):
    return [random.randint(0, 4) for _ in range(longitud)]
```

#### ¿Por qué es importante?

| Solo aleatorio | Con semillas |
|----------------|--------------|
| Convergencia lenta | Convergencia más rápida |
| Desperdicia generaciones | Ya tiene base buena |
| Puede estancarse | Diversidad inicial |

---

### 2.3 Evaluación (Fitness)

#### ¿Qué es?

Es **medir qué tan bueno es cada individuo**. Se simula el juego completo con la secuencia de acciones y se calcula una puntuación.

#### Fórmula de Fitness

```
fitness = (altura_suelo × 1.0) + (altura_aire × 0.5) + (waypoints × 200)
          - (caída × 2) - (idle × 0.5) - (stuck × 1.0) - (fallback × 1.0)
```

#### Desglose de Componentes

| Componente | Fórmula | Peso | Descripción |
|------------|---------|------|-------------|
| `altura_suelo` | `suelo_y - altura_max_suelo` | ×1.0 | Distancia vertical máxima estando en suelo |
| `altura_aire` | `suelo_y - altura_max_aire` | ×0.5 | Distancia vertical máxima en el aire |
| `waypoints` | `count(waypoints_visitados) × 200` | +200 c/u | Bonus por pasar puntos de control |
| `caída` | `altura_actual - altura_max` si bajó | ×2.0 | Penalización por caer |
| `idle` | `total_idle_frames × 0.5` | ×0.5 | Penalización por quedarse quieto |
| `stuck` | `total_stuck_frames × 1.0` | ×1.0 | Penalización por chocar contra paredes |
| `fallback` | `total_fallback_frames × 1.0` | ×1.0 | Penalización por bajar de altura |

#### Ejemplo de Cálculo

```
SIMULACIÓN:
- Altura máxima suelo: 450px arriba del spawn
- Altura máxima aire: 500px arriba del spawn
- Waypoints visitados: [0, 1, 3] → 3 waypoints
- Frames idle: 120
- Frames atascado: 15
- Frames cayendo: 8

CÁLCULO:
fitness = (450 × 1.0)     ← altura suelo
        + (500 × 0.5)     ← altura aire
        + (3 × 200)       ← waypoints
        - (0 × 2)         ← caída (no cayó)
        - (120 × 0.5)     ← idle
        - (15 × 1.0)      ← stuck
        - (8 × 1.0)       ← fallback

fitness = 450 + 250 + 600 - 0 - 60 - 15 - 8
fitness = 1217
```

#### ¿Por qué es importante?

| Sin evaluación | Con evaluación |
|----------------|----------------|
| No sabemos quién es mejor | Sabemos exactamente quién es mejor |
| Búsqueda a ciegas | Tenemos una "brújula" |
| No hay evolución | Permite selección natural |

---

### 2.4 Selección por Torneo

#### ¿Qué es?

Es **elegir qué individuos se reproducen** basándose en competencias entre subgrupos pequeños.

#### Parámetros

- **k = 3**: Tamaño del torneo (3 competidores por torneo)
- **n = 5**: Número de torneos (5 ganadores para padres)

#### Algoritmo

```python
# evolutivo.py:344-351
def seleccionar_por_torneo(poblacion, fitnesses, k=3, n=5):
    ganadores = []
    indices = list(range(len(poblacion)))
    
    for _ in range(n):
        # 1. Seleccionar k individuos al azar
        candidatos = random.sample(indices, min(k, len(indices)))
        
        # 2. El de mayor fitness gana
        mejor_candidato = max(candidatos, key=lambda i: fitnesses[i])
        
        # 3. Agregar ganador a la lista de padres
        ganadores.append(poblacion[mejor_candidato])
    
    return ganadores
```

#### Ejemplo Visual

```
POBLACIÓN (100 individuos):
[A:1217] [B:340] [C:890] [D:1100] [E:560] [F:980] [G:950] [H:920] ...

TORNEO 1 (k=3):
┌─────────────────────────────────┐
│  Candidatos: [C:890, E:560, A:1217] │
│                                  │
│  Comparar:                       │
│  C:890 vs E:560 → C gana        │
│  C:890 vs A:1217 → A gana       │
│                                  │
│  Ganador: A:1217                │
└─────────────────────────────────┘

TORNEO 2 (k=3):
┌─────────────────────────────────┐
│  Candidatos: [B:340, F:980, D:1100] │
│                                  │
│  Ganador: D:1100                │
└─────────────────────────────────┘

... (5 torneos en total)

PADRES SELECCIONADOS: [A, D, A, ...]
```

#### Comparación con Otros Métodos

| Método | Probabilidad del mejor | Probabilidad del peor | Presión selectiva |
|--------|------------------------|----------------------|-------------------|
| **Aleatoria** | 1/100 = 1% | 1/100 = 1% | Ninguna |
| **Torneo (k=3)** | ~27% | ~3% | Moderada |
| **Torneo (k=5)** | ~40% | ~0.8% | Alta |
| **Proporcional (ruleta)** | ~40% | ~11% | Muy alta |

#### ¿Por qué es importante?

| Selección aleatoria | Selección por torneo |
|---------------------|----------------------|
| No hay presión selectiva | Los mejores tienen ventaja |
| Evolución muy lenta | Evolución balanceada |
| Puede tardar mucho | Convergencia razonable |

---

### 2.5 Operadores Genéticos

#### 2.5.1 Cruce (Recombinación)

##### ¿Qué es?

Combinar el material genético de dos padres para crear un hijo.

##### Algoritmo de Cruce de Un Punto

```python
# evolutivo.py:338-341
def cruzar_secuencias(padre1, padre2):
    punto = random.randint(1, len(padre1) - 1)
    hijo = padre1[:punto] + padre2[punto:]
    return hijo
```

##### Ejemplo Visual

```
PADRE 1: [2, 0, 0, 4, | 0, 0, 1, 0, 0, 3]
PADRE 2: [1, 0, 0, 3, | 0, 0, 2, 0, 0, 4]
HIJO:    [2, 0, 0, 4,   0, 0, 2, 0, 0, 4]
```

##### Tipos de Cruce

```python
# CRUCE DE UN PUNTO (el usado)
hijo = padre1[:punto] + padre2[punto:]

# CRUCE DE DOS PUNTOS
punto1, punto2 = sorted(random.sample(range(len(padre1)), 2))
hijo = padre1[:punto1] + padre2[punto1:punto2] + padre1[punto2:]

# CRUCE UNIFORME
hijo = [p1[i] if random.random() < 0.5 else p2[i] for i in range(len(p1))]
```

---

#### 2.5.2 Mutación Individual

##### ¿Qué es?

Cambiar aleatoriamente algunos genes del cromosoma.

##### Algoritmo

```python
# evolutivo.py:316-321
def mutar_secuencia(secuencia, tasa_mutacion=0.2):
    nueva = secuencia.copy()
    for i in range(len(nueva)):
        if random.random() < tasa_mutacion:
            nueva[i] = random.randint(0, 4)
    return nueva
```

##### Ejemplo Visual

```
ORIGINAL:  [2, 0, 0, 4, 0, 0, 1, 0, 0, 3]
MUTADO:    [3, 0, 0, 1, 0, 0, 1, 0, 0, 3]
           ↑           ↑
          Cambió     Cambió
```

---

#### 2.5.3 Mutación por Segmentos

##### ¿Qué es?

Cambiar segmentos completos de acciones a un mismo valor.

##### Algoritmo

```python
# evolutivo.py:323-335
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
```

---

### 2.6 Elitismo

#### ¿Qué es?

Es **preservar los mejores individuos** directamente en la siguiente generación sin modificarlos.

#### Algoritmo

```python
# evolutivo.py:463-468
indices_ordenados = sorted(range(len(fitnesses)), 
                          key=lambda i: fitnesses[i], 
                          reverse=True)
elites_directas = [poblacion[i] for i in indices_ordenados[:elites]]
nueva_poblacion = elites_directas.copy()
```

#### Ejemplo Visual

```
POBLACIÓN ACTUAL (100 individuos):
┌─────────────────────────────────────────────┐
│  #1  A: fitness=1217  ← ÉLITE               │
│  #2  D: fitness=1100  ← ÉLITE               │
│  #3  F: fitness=980   ← ÉLITE               │
│  #4  G: fitness=950   ← ÉLITE               │
│  #5  H: fitness=920   ← ÉLITE               │
│  ... (95 más)                               │
└─────────────────────────────────────────────┘
                        ↓
NUEVA POBLACIÓN (100 individuos):
┌─────────────────────────────────────────────┐
│  ÉLITES (copias idénticas):                 │
│  A: fitness=1217  ← MISMO INDIVIDUO         │
│  D: fitness=1100  ← MISMO INDIVIDUO         │
│  F: fitness=980   ← MISMO INDIVIDUO         │
│  G: fitness=950   ← MISMO INDIVIDUO         │
│  H: fitness=920   ← MISMO INDIVIDUO         │
│                                             │
│  RESTO (95 individuos nuevos):              │
│  - Hijos de cruce                           │
│  - Individuos mutados                       │
│  - Nuevos aleatorios                        │
└─────────────────────────────────────────────┘
```

#### ¿Por qué es importante?

| Sin elitismo | Con elitismo |
|--------------|--------------|
| El mejor puede desaparecer | El mejor siempre sobrevive |
| Fitness puede bajar | Fitness nunca baja |
| Convergencia inestable | Convergencia garantizada |

---

### 2.7 Mutación Adaptativa

#### ¿Qué es?

Es **ajustar automáticamente la tasa de mutación** según si el algoritmo está progresando o estancado.

#### Lógica

```
SI hay mejora → BAJAR mutación (explotar lo que funciona)
SI no hay mejora → SUBIR mutación (explorar nuevas soluciones)
```

#### Algoritmo

```python
# evolutivo.py:432-452
if mejor_fitness_gen > mejor_fitness_global:
    tasa_mutacion_actual = tasa_mutacion * 0.9
    generaciones_sin_mejora = 0
else:
    generaciones_sin_mejora += 1
    if generaciones_sin_mejora > 10:
        tasa_mutacion_actual = min(
            tasa_mutacion * 2.0,
            tasa_mutacion_actual * 1.1
        )
```

#### Ejemplo Temporal

```
Generación  Mutación    Fitness    Acción
─────────────────────────────────────────────
    1        0.300       450       Inicio
    5        0.270       620       Mejora → Baja ↓
   10        0.243       780       Mejora → Baja ↓
   15        0.219       780       Sin mejora
   20        0.219       780       Sin mejora
   25        0.219       780       Sin mejora
   30        0.219       780       Sin mejora (10 gens)
   31        0.241       780       Mutación sube ↑
   35        0.265       780       Mutación sube ↑
   40        0.239       950       Mejora ↓ (mutación baja)
```

#### ¿Por qué es importante?

| Mutación fija | Mutación adaptativa |
|---------------|---------------------|
| Si es alta: nunca converge | Se ajusta automáticamente |
| Si es baja: se estanca | Explora cuando está estancado |
| Requiere ajuste manual | Equilibra exploración/explotación |

---

### 2.8 Reinicio Parcial

#### ¿Qué es?

Reemplazar un porcentaje de la población con individuos aleatorios cuando hay estancamiento prolongado.

#### Algoritmo

```python
# evolutivo.py:484-488
if generaciones_sin_mejora > 0 and generaciones_sin_mejora % 20 == 0:
    n_restart = max(1, tamano_poblacion // 10)
    for i in range(n_restart):
        idx = -(i + 1)
        nueva_poblacion[idx] = crear_secuencia_aleatoria(longitud_secuencia)
```

#### ¿Por qué es importante?

| Sin reinicio | Con reinicio |
|--------------|--------------|
| Puede estancarse para siempre | Introduce diversidad |
| Pérdida de diversidad genética | Mantiene exploración |
| Riesgo de convergencia prematura | Escape de óptimos locales |

---

## 3. Flujo Completo del Algoritmo

### 3.1 Diagrama de Flujo

```
┌─────────────────────────────────────────────────────────┐
│                    INICIO                                │
└─────────────────┬───────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────┐
│  1. CREAR POBLACIÓN INICIAL                             │
│     - 6 semillas inteligentes                           │
│     - 94 individuos aleatorios                          │
│     - Total: 100 individuos                             │
└─────────────────┬───────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────┐
│  2. EVALUAR CADA INDIVIDUO (FITNESS)                    │
│     - Simular secuencia completa                        │
│     - Medir altura, waypoints, idle, stuck, fallback    │
│     - Calcular puntuación con fórmula                   │
└─────────────────┬───────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────┐
│  3. VERIFICAR MEJORA                                    │
│     - ¿Nuevo mejor fitness?                             │
│     - Si sí: actualizar mejor global, bajar mutación    │
│     - Si no: incrementar contador sin mejora            │
└─────────────────┬───────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────┐
│  4. SELECCIONAR PADRES (TORNEO k=3)                     │
│     - 5 torneos                                         │
│     - 3 competidores por torneo                         │
│     - 5 ganadores (padres)                              │
└─────────────────┬───────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────┐
│  5. CREAR NUEVA POBLACIÓN                               │
│     a) Copiar élites directas (top 5)                   │
│     b) Para el resto:                                   │
│        - 50% probabilidad: mutar padre                  │
│        - 50% probabilidad: cruzar 2 padres + mutar      │
└─────────────────┬───────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────┐
│  6. APLICAR REINICIO PARCIAL (si aplica)                │
│     - Cada 20 generaciones sin mejora                   │
│     - Reemplazar 10% con aleatorios                     │
└─────────────────┬───────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────┐
│  7. ¿GENERACIONES RESTANTES?                            │
│     - Sí → Volver al paso 2                             │
│     - No → Guardar mejor secuencia                      │
└─────────────────┬───────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────┐
│  8. RESULTADO FINAL                                     │
│     - Guardar mejor_secuencia.txt                       │
│     - Mostrar estadísticas finales                      │
└─────────────────────────────────────────────────────────┘
```

---

## 4. Librerías Utilizadas

### 4.1 Para el Algoritmo Evolutivo

| Librería | Tipo | Uso en el Proyecto |
|----------|------|-------------------|
| `random` | Estándar | Selección, mutación, cruce |
| `multiprocessing` | Estándar | Evaluación paralela |
| `json` | Estándar | Guardar resultados |
| `os` | Estándar | Detectar CPU cores |
| `time` | Estándar | Medir tiempo de ejecución |

### 4.2 Para la Simulación del Juego

| Librería | Tipo | Uso en el Proyecto |
|----------|------|-------------------|
| `pygame` | Externa | Renderizado y física del juego |

### 4.3 Para el Enfoque RL (otro algoritmo)

| Librería | Tipo | Uso en el Proyecto |
|----------|------|-------------------|
| `gymnasium` | Externa | Entorno de RL |
| `stable-baselines3` | Externa | Algoritmos RL (PPO, etc.) |
| `torch` | Externa | Redes neuronales |
| `numpy` | Externa | Operaciones matriciales |
| `tensorboard` | Externa | Visualización de métricas |

### 4.4 Comparación de Enfoques

```
ENFOQUE EVOLUTIVO (evolutivo.py):
┌─────────────────────────────────────────────┐
│  Librerías: random, multiprocessing, json   │
│  Complejidad: Baja                          │
│  Dependencias: Mínimas                      │
│  Instalación: No requiere pip install       │
└─────────────────────────────────────────────┘

ENFOQUE RL (Trainning vs evaluation/):
┌─────────────────────────────────────────────┐
│  Librerías: torch, stable-baselines3,       │
│             gymnasium, numpy, tensorboard   │
│  Complejidad: Alta                          │
│  Dependencias: Muchas                       │
│  Instalación: Requiere pip install          │
└─────────────────────────────────────────────┘
```

---

## 5. Análisis de Complejidad

### 5.1 Complejidad Temporal

#### Por Generación

```
EVALUACIÓN:
  - Población: N individuos
  - Cada individuo: L acciones × F frames
  - Por generación: O(N × L × F)

SELECCIÓN:
  - Torneos: k competidores × n torneos
  - Por generación: O(k × n) ≈ O(1) (constante)

REPRODUCCIÓN:
  - N individuos a crear
  - Cruce/mutación: O(L) por individuo
  - Por generación: O(N × L)

TOTAL POR GENERACIÓN:
  O(N × L × F) + O(N × L) = O(N × L × F)
```

#### Por Ejecución Completa

```
GENERACIONES: G
TOTAL = G × O(N × L × F) = O(G × N × L × F)

CON VALORES TÍPICOS:
  G = 1000 generaciones
  N = 100 individuos
  L = 750 acciones
  F = 30 frames/acción

  TOTAL ≈ 1000 × 100 × 750 × 30 = 2,250,000,000 operaciones
  ≈ 2.25 × 10⁹ operaciones
```

#### Con Paralelismo

```python
# evolutivo.py:401-408
if usar_paralelo and tamano_poblacion > 5:
    with multiprocessing.Pool(processes=min(os.cpu_count(), tamano_poblacion)) as pool:
        resultados = pool.map(_evaluar_individual, args_list)
```

```
SIN PARALELO:
  Tiempo = N × (L × F) = 100 × 22500 = 2,250,000 frames

CON PARALELO (8 cores):
  Tiempo = (N/8) × (L × F) = 12.5 × 22500 = 281,250 frames
  Speedup: ~8x
```

### 5.2 Complejidad Espacial

```
POBLACIÓN:
  - N individuos × L acciones × 4 bytes/int
  - 100 × 750 × 4 = 300,000 bytes ≈ 300 KB

FITNESS:
  - N floats
  - 100 × 8 = 800 bytes

TOTAL:
  ≈ 301 KB para datos principales

CON PARALELIZACIÓN:
  - Cada proceso necesita copia de animaciones
  - 8 procesos × ~5 MB = 40 MB
```

---

## 6. Ventajas y Desventajas

### 6.1 Ventajas del Algoritmo Evolutivo

| Ventaja | Descripción |
|---------|-------------|
| **Simple de implementar** | No requiere math compleja (gradientes, etc.) |
| **Pocas dependencias** | Solo random, multiprocessing |
| **Paralelizable** | Cada individuo se evalúa independientemente |
| **No necesita gradientes** | Funciona con funciones de fitness no diferenciables |
| **Exploración amplia** | Puede encontrar soluciones muy diversas |
| **Robusto** | No se estanca fácilmente (con mutación adaptativa) |

### 6.2 Desventajas del Algoritmo Evolutivo

| Desventaja | Descripción |
|------------|-------------|
| **Lento** | Muchas evaluaciones necesarias |
| **No óptimo garantizado** | Puede encontrar óptimos locales |
| **Sin aprendizaje** | No "aprende" como RL, solo busca |
| **Muchas evaluaciones** | Cada individuo requiere simulación completa |
| **Parámetros sensibles** | Mutación, población, etc. afectan mucho |

### 6.3 Comparación con Otros Algoritmos

| Algoritmo | Velocidad | Óptimo | Paralelizable | Complejidad |
|-----------|-----------|--------|---------------|-------------|
| **Evolutivo** | Lento | Local | ✅ Sí | Baja |
| **Q-Learning** | Medio | Global (tabular) | ❌ No | Media |
| **DQN** | Lento | Global (aprox.) | ⚠️ Parcial | Alta |
| **PPO** | Lento | Global (aprox.) | ⚠️ Parcial | Alta |
| **Policy Gradient** | Lento | Global (aprox.) | ⚠️ Parcial | Alta |

### 6.4 Cuándo Usar Cada Algoritmo

```
USAR EVOLUTIVO CUANDO:
  ✅ No hay gradientes disponibles
  ✅ La función de fitness es compleja/no diferenciable
  ✅ Se necesita paralelización masiva
  ✅ El problema es de optimización de parámetros
  ✅ No se requiere aprendizaje en línea

USAR RL (Q-Learning, PPO, etc.) CUANDO:
  ✅ Hay recompensas claras por timestep
  ✅ El agente debe aprender de la interacción
  ✅ Se necesita aprendizaje en línea
  ✅ El problema es secuencial/markoviano
  ✅ Se requiere generalización
```

---

## 7. Código Relevante

### 7.1 Función de Fitness Completa

```python
# fitness.py
def calcular_fitness(
    altura_maxima_suelo,
    altura_maxima_aires,
    waypoints_visitados,
    altura_actual_suelo,
    total_idle_frames=0,
    total_stuck_frames=0,
    total_fallback_frames=0,
):
    fitness_suelo = constantes.suelo_y - altura_maxima_suelo
    fitness_aire = constantes.suelo_y - altura_maxima_aires
    waypoint_bonus = len(waypoints_visitados) * 200
    
    caida = altura_actual_suelo - altura_maxima_suelo if altura_actual_suelo > altura_maxima_suelo else 0
    idle_penalty = total_idle_frames * 0.5
    wall_penalty = total_stuck_frames * 1.0
    fallback_penalty = total_fallback_frames * 1.0
    
    fitness = (fitness_suelo * 1.0 + fitness_aire * 0.5 + waypoint_bonus
               - caida * 2 - idle_penalty - wall_penalty - fallback_penalty)
    
    return max(0, fitness), {...}
```

### 7.2 Selección por Torneo

```python
# evolutivo.py:344-351
def seleccionar_por_torneo(poblacion, fitnesses, k=3, n=5):
    ganadores = []
    indices = list(range(len(poblacion)))
    for _ in range(n):
        candidatos = random.sample(indices, min(k, len(indices)))
        mejor_candidato = max(candidatos, key=lambda i: fitnesses[i])
        ganadores.append(poblacion[mejor_candidato])
    return ganadores
```

### 7.3 Cruce

```python
# evolutivo.py:338-341
def cruzar_secuencias(padre1, padre2):
    punto = random.randint(1, len(padre1) - 1)
    hijo = padre1[:punto] + padre2[punto:]
    return hijo
```

### 7.4 Mutación Individual

```python
# evolutivo.py:316-321
def mutar_secuencia(secuencia, tasa_mutacion=0.2):
    nueva = secuencia.copy()
    for i in range(len(nueva)):
        if random.random() < tasa_mutacion:
            nueva[i] = random.randint(0, 4)
    return nueva
```

### 7.5 Mutación por Segmentos

```python
# evolutivo.py:323-335
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
```

### 7.6 Bucle Principal del Algoritmo

```python
# evolutivo.py:400-490
for gen in range(generaciones):
    # 1. Evaluar población
    fitnesses = []
    for secuencia in poblacion:
        fitness, altura_suelo, _ = juego.evaluar_secuencia(secuencia, frames_por_accion)
        fitnesses.append(fitness)
    
    # 2. Verificar mejora
    mejor_idx = fitnesses.index(max(fitnesses))
    mejor_fitness_gen = fitnesses[mejor_idx]
    
    if mejor_fitness_gen > mejor_fitness_global:
        mejor_fitness_global = mejor_fitness_gen
        mejor_secuencia_global = poblacion[mejor_idx].copy()
        tasa_mutacion_actual = tasa_mutacion * 0.9
        generaciones_sin_mejora = 0
    else:
        generaciones_sin_mejora += 1
        if generaciones_sin_mejora > 10:
            tasa_mutacion_actual = min(tasa_mutacion * 2.0, tasa_mutacion_actual * 1.1)
    
    # 3. Seleccionar padres
    padres_torneo = seleccionar_por_torneo(poblacion, fitnesses, k=3, n=padres)
    
    # 4. Crear nueva población
    indices_ordenados = sorted(range(len(fitnesses)), key=lambda i: fitnesses[i], reverse=True)
    elites_directas = [poblacion[i] for i in indices_ordenados[:elites]]
    nueva_poblacion = elites_directas.copy()
    
    while len(nueva_poblacion) < tamano_poblacion:
        if random.random() < 0.5:
            padre = random.choice(padres_torneo)
            if random.random() < 0.5:
                hijo = mutar_secuencia(padre, tasa_mutacion_actual)
            else:
                hijo = mutar_por_segmentos(padre, tasa_mutacion_actual)
        else:
            padre1 = random.choice(padres_torneo)
            padre2 = random.choice(padres_torneo)
            hijo = cruzar_secuencias(padre1, padre2)
            hijo = mutar_secuencia(hijo, tasa_mutacion_actual * 0.5)
        nueva_poblacion.append(hijo)
    
    # 5. Reinicio parcial
    if generaciones_sin_mejora > 0 and generaciones_sin_mejora % 20 == 0:
        n_restart = max(1, tamano_poblacion // 10)
        for i in range(n_restart):
            idx = -(i + 1)
            nueva_poblacion[idx] = crear_secuencia_aleatoria(longitud_secuencia)
    
    poblacion = nueva_poblacion
```

---

## 8. Conclusiones

### 8.1 Resumen del Algoritmo

El proyecto implementa un **algoritmo genético clásico** con las siguientes características:

1. **Representación**: Secuencias de acciones (0-4)
2. **Evaluación**: Simulación completa del juego
3. **Selección**: Torneo con k=3
4. **Reproducción**: Cruce de un punto + mutación
5. **Elitismo**: Top 5 sobreviven intactos
6. **Adaptación**: Mutación adaptativa según progreso
7. **Diversidad**: Reinicio parcial cada 20 gens sin mejora

### 8.2 Fortalezas

- ✅ Simple y fácil de entender
- ✅ Paralelizable (multiprocessing)
- ✅ No necesita librerías externas complejas
- ✅ Robusto con mutación adaptativa
- ✅ Encuentra soluciones viables

### 8.3 Debilidades

- ⚠️ Lento (muchas evaluaciones)
- ⚠️ No garantiza óptimo global
- ⚠️ Parámetros sensibles
- ⚠️ No aprende como RL

### 8.4 Posibles Mejoras

1. **Cruce de dos puntos** para mayor diversidad
2. **Mutación gaussiana** para exploración continua
3. **Niching** para mantener diversidad
4. **Algoritmos evolutivos evolutivos** (EPA) para auto-ajuste
5. **Híbrido RL + Evolutivo** para aprovechar lo mejor de ambos

### 8.5 Aplicaciones

Este algoritmo es aplicable a:

- 🎮 Optimización de estrategias de videojuegos
- 🤖 Control de robots
- 📊 Optimización de parámetros
- 🧬 Problemas de ingeniería
- 💰 Optimización financiera

---

## Referencias

- Código fuente: `evolutivo.py`, `fitness.py`
- Documentación del proyecto: `# Diseño del Agente de Reinforcemen.md`
- Comparación con RL: `Trainning vs evaluation/`

---

*Documento generado para estudio y análisis del algoritmo evolutivo implementado en el proyecto Jump King.*

---

## 9. Resultados Empíricos

### 9.1 Tabla Comparativa Completa de Todas las Versiones

| Versión | Gen | Acciones | Fitness | Altura | Progreso | Tiempo (s) | Notas |
|---------|-----|----------|---------|--------|----------|------------|-------|
| v.1.3 | 500 | 1000 | 1,242.0 | 960px | 33.1% | 2,288 | Mejor progreso relativo |
| v.1.4 | 500 | 1000 | 1,868.0 | 820px | 28.3% | 2,959 | |
| v.1.5 | 500 | 1000 | 1,277.0 | 570px | 19.7% | 2,978 | |
| v.1.5 (fake) | 500 | 1000 | 1,693.0 | 400px | 13.8% | 2,957 | ⚠️ Fake |
| v.1.6 | 500 | 1000 | 1,952.0 | 820px | 28.3% | 3,013 | |
| v.1.7 | 1000 | 500 | 1,688.0 | 500px | 17.2% | 6,275 | |
| v.1.8 | 1000 | 500 | 1,500.0 | 310px | 10.7% | 6,340 | |
| v.1.9 | 1000 | 500 | 2,010.0 | 820px | 28.3% | 6,064 | |
| v.1.9.1 | - | - | 2,010.0 | 820px | 28.3% | - | Solo evaluación |
| v.2.1 | 1000 | 500 | 7,694.0 | 20px | 0.7% | 4,424 | ⚠️ Overfitting |
| v.2.1 (fake) | 1000 | 500 | 6,302.0 | 220px | 7.6% | 4,514 | ⚠️ Fake |
| v.2.2 | 1000 | - | 2,938.0 | 870px | 30.0% | 4,562 | |
| v.2.3 | 1000 | - | 3,529.0 | 820px | 28.3% | 5,299 | |
| v.2.4 | 1000 | 750 | 3,345.0 | 820px | 28.3% | 6,998 | ⚠️ Overfitting |
| v.2.5 | 1000 | 10 | 2,693.0 | 590px | 20.3% | 139 | Muy rápido |
| v.2.6 | 1000 | - | 3,884.0 | 820px | 28.3% | 686 | |
| v.2.7 | 1000 | 30 | 3,943.0 | 820px | 28.3% | 2,052 | **Mejor absoluto** |

---

### 9.2 Gráfica ASCII - Fitness por Versión

```
FITNESS POR VERSIÓN (escala: 1 bloque = 200 unidades)
═══════════════════════════════════════════════════════════════════════════════════

v.1.3    ███████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  1,242
v.1.4    ███████████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░  1,868
v.1.5    ███████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  1,277
v.1.5(f) ██████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  1,693 ⚠️
v.1.6    ████████████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░  1,952
v.1.7    ██████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  1,688
v.1.8    ███████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  1,500
v.1.9    █████████████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░  2,010
v.2.1    █████████████████████████████████████████████████████████████████████████████████  7,694 ⚠️
v.2.1(f) ████████████████████████████████████████████████████████████░░░░░  6,302 ⚠️
v.2.2    ████████████████████████████████████████████████████░░░░░░░░░░░░░  2,938
v.2.3    ███████████████████████████████████████████████████████████░░░░░░  3,529
v.2.4    █████████████████████████████████████████████████████████░░░░░░░░  3,345 ⚠️
v.2.5    ███████████████████████████████████████████████░░░░░░░░░░░░░░░░░░  2,693
v.2.6    ███████████████████████████████████████████████████████████████░░  3,884
v.2.7    █████████████████████████████████████████████████████████████████░  3,943 ★ MEJOR

         └──────────────────────────────────────────────────────────────────────────┘
         0              2,000              4,000              6,000              8,000
```

---

### 9.3 Gráfica ASCII - Progreso Alcanzado

```
PROGRESO (% del mapa completado)
═══════════════════════════════════════════════════════════════════════════════════

v.1.3    ██████████████████████████████████████████████████████████████████  33.1% ★ MEJOR
v.1.4    █████████████████████████████████████████████████████████░░░░░░░░  28.3%
v.1.5    ███████████████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░  19.7%
v.1.5(f) ██████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  13.8% ⚠️
v.1.6    █████████████████████████████████████████████████████████░░░░░░░░  28.3%
v.1.7    ██████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  17.2%
v.1.8    ██████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  10.7%
v.1.9    █████████████████████████████████████████████████████████░░░░░░░░  28.3%
v.2.1    ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   0.7% ⚠️
v.2.1(f) ██████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   7.6% ⚠️
v.2.2    ███████████████████████████████████████████████████████████████░░  30.0%
v.2.3    █████████████████████████████████████████████████████████░░░░░░░░  28.3%
v.2.4    █████████████████████████████████████████████████████████░░░░░░░░  28.3% ⚠️
v.2.5    ███████████████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░  20.3%
v.2.6    █████████████████████████████████████████████████████████░░░░░░░░  28.3%
v.2.7    █████████████████████████████████████████████████████████░░░░░░░░  28.3%

         └──────────────────────────────────────────────────────────────────────────┘
         0%                 10%                20%                30%                35%
```

---

### 9.4 Tabla de Eficiencia (Fitness/Segundo)

| Versión | Fitness | Tiempo (s) | Eficiencia (f/s) | Ranking |
|---------|---------|------------|------------------|---------|
| v.2.5 | 2,693 | 139 | **19.37** | 🥇 1° |
| v.2.6 | 3,884 | 686 | 5.66 | 🥈 2° |
| v.2.7 | 3,943 | 2,052 | 1.92 | 🥉 3° |
| v.1.3 | 1,242 | 2,288 | 0.54 | 4° |
| v.1.4 | 1,868 | 2,959 | 0.63 | 5° |
| v.1.6 | 1,952 | 3,013 | 0.65 | 6° |
| v.2.1 | 7,694 | 4,424 | 1.74 | ⚠️ |
| v.2.4 | 3,345 | 6,998 | 0.48 | ⚠️ |

---

### 9.5 Análisis de Overfitting

| Versión | Fitness Entrenamiento | Fitness Evaluación | Diferencia | Estado |
|---------|----------------------|-------------------|------------|--------|
| v.1.9 | 2,010.0 | 2,010.0 | 0.0 | ✅ Consistente |
| v.2.1 | 7,694.0 | ~0.0 | -7,694.0 | ❌ Overfitting |
| v.2.4 | 3,345.0 | 0.0 | -3,345.0 | ❌ Overfitting |

**Problema detectado:** Las versiones con fitness muy alto en entrenamiento pero 0 en evaluación indican que el algoritmo está **memorizando** la secuencia en lugar de **generalizar**.

---

### 9.6 Conclusiones Empíricas

1. **Mejor progreso:** v.1.3 (33.1%) - Parámetros: 500 gen, 50 pob, 1000 acc
2. **Mayor fitness absoluto:** v.2.7 (3,943) - Parámetros: 1000 gen, 100 pob, 30 acc
3. **Más eficiente:** v.2.5 (19.37 f/s) - Parámetros: 1000 gen, 100 pob, 10 acc
4. **Más estable:** v.1.9 - Fitness consistente entre entrenamiento/evaluación
5. **Problema principal:** Overfitting en versiones 2.x (fitness alto en entrenamiento, 0 en evaluación)
