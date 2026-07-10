# 🎮 Proyecto Evolutivo - Jump King

## Presentación del Algoritmo Genético

---

## 📋 Agenda

1. Introducción al Proyecto
2. Componentes del Algoritmo
3. Flujo del Algoritmo
4. Resultados Empíricos
5. Conclusiones

---

## 1. Introducción

### ¿Qué es un Algoritmo Evolutivo?

Un **algoritmo evolutivo** es una técnica de optimización inspirada en la **selección natural de Darwin**. Utiliza mecanismos como reproducción, mutación y selección para evolucionar soluciones a problemas complejos.

### ¿Cómo funciona?

```
POBLACIÓN INICIAL → EVALUAR → SELECCIONAR MEJORES → REPRODUCIR → NUEVA POBLACIÓN
         ↑                                                              │
         └──────────────────────────────────────────────────────────────┘
```

El algoritmo itera generación tras generación, mejorando progresivamente las soluciones hasta encontrar una óptima.

### Aplicación en Jump King

**Jump King** - Juego de plataformas donde el personaje escala verticalmente saltando entre plataformas.

### Objetivo

Encontrar una **secuencia óptima de acciones** que maximice la altura alcanzada:

```
Cromosoma = [a₁, a₂, ..., aₙ]  donde aᵢ ∈ {0, 1, 2, 3, 4}
```

### Representación del Problema

| Acción | Significado |
|--------|-------------|
| `0` | Idle |
| `1` | Salto alto izquierda |
| `2` | Salto alto derecha |
| `3` | Salto bajo izquierda |
| `4` | Salto bajo derecha |

**Ejemplo:**
```
[2, 0, 0, 4, 0, 0, 1, 0, 0, 3, 2, ...]
 ↑     ↑     ↑     ↑     ↑     ↑
Salto  Idle  Salto  Idle  Salto  Idle
```

---

## 2. Componentes del Algoritmo

### 2.1 ¿Qué es un Cromosoma?

Un **cromosoma** representa una solución completa al problema. En Jump King, es una **secuencia de acciones** que el personaje debe realizar.

- **Estructura:** Lista de enteros (longitud: 750 acciones)
- **Valores:** {0, 1, 2, 3, 4}

---

### 2.2 ¿Qué es una Población?

La **población** es el conjunto de **individuos** (cromosomas) que compiten entre sí. Se evalúan, se reproducen y evolucionan generación tras generación.

**Población inicial:** 100 individuos con semillas inteligentes:

```python
semillas = [
    crear_secuencia_inteligente,  # Patrón predefinido
    crear_secuencia_espiral,       # Movimiento circular
    crear_secuencia_pasos,         # Patrón rítmico
]
```

| Estrategia | Convergencia |
|------------|--------------|
| Solo aleatorio | Lenta |
| Con semillas | Más rápida |

---

### 2.3 ¿Qué es el Fitness?

El **fitness** es una **medida de calidad** que indica qué tan bueno es cada individuo. Es como un puntaje que determina quién "sobrevive" y quién se reproduce.

**Fórmula:**
```
fitness = (altura_suelo × 1.0) + (altura_aire × 0.5) + (waypoints × 200)
          - (caída × 2) - (idle × 0.5) - (stuck × 1.0) - (fallback × 1.0)
```

**Ejemplo:**
```
Altura máxima suelo: 450px
Altura máxima aire: 500px
Waypoints: 3

fitness = 450 + 250 + 600 = 1,217
```

---

### 2.4 ¿Qué es la Selección por Torneo?

Es el método para **elegir qué individuos se reproducen**. Se forman pequeños grupos (torneos) y el de mayor fitness gana.

| Parámetro | Valor |
|-----------|-------|
| k (tamaño torneo) | 3 |
| n (número torneos) | 5 |

```
TORNEO: [C:890, E:560, A:1217] → Ganador: A:1217
```

---

### 2.5 ¿Qué son los Operadores Genéticos?

Son las herramientas que permiten **crear nuevos individuos** combinando o modificando a los padres.

#### Cruce (Recombinación)
Combina el material genético de dos padres para crear un hijo.
```python
hijo = padre1[:punto] + padre2[punto:]
```
```
PADRE1: [2, 0, 0, 4, | 0, 0, 1, 0, 0, 3]
PADRE2: [1, 0, 0, 3, | 0, 0, 2, 0, 0, 4]
HIJO:   [2, 0, 0, 4,   0, 0, 2, 0, 0, 4]
```

---

### 2.6 ¿Qué es la Mutación?

La **mutación** es un cambio aleatorio en los genes de un individuo. Sirve para **explorar nuevas soluciones** y evitar estancamientos.

#### Mutación Individual
Cambia genes uno por uno.
```python
if random.random() < tasa_mutacion:
    nueva[i] = random.randint(0, 4)
```

#### Mutación por Segmentos
Cambia segmentos completos a un mismo valor.

---

### 2.7 ¿Qué es el Elitismo?

El **elitismo** es el mecanismo que **preserva los mejores individuos** directamente en la siguiente generación sin modificarlos.

**Top 5** sobreviven intactos en cada generación.

| Sin elitismo | Con elitismo |
|--------------|--------------|
| Mejor puede desaparecer | Mejor siempre sobrevive |
| Fitness puede bajar | Fitness nunca baja |

---

### 2.8 Mutación Adaptativa

Se ajusta automáticamente según el progreso:

```
SI hay mejora → BAJAR mutación (explotar)
SI no hay mejora → SUBIR mutación (explorar)
```

| Mutación fija | Mutación adaptativa |
|---------------|---------------------|
| Si es alta: nunca converge | Se ajusta automáticamente |
| Si es baja: se estanca | Equilibra exploración/explotación |

---

### 2.9 Reinicio Parcial

Cada **20 generaciones sin mejora**, reemplazar **10%** con aleatorios para mantener diversidad.

---

## 3. Flujo del Algoritmo

```
┌─────────────────────────────────────────────────────────┐
│                    INICIO                                │
└─────────────────┬───────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────┐
│  1. CREAR POBLACIÓN INICIAL                             │
│     - 6 semillas inteligentes                           │
│     - 94 individuos aleatorios                          │
└─────────────────┬───────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────┐
│  2. EVALUAR CADA INDIVIDUO (FITNESS)                    │
└─────────────────┬───────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────┐
│  3. VERIFICAR MEJORA                                    │
│     - Actualizar mejor global                           │
│     - Ajustar mutación adaptativa                       │
└─────────────────┬───────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────┐
│  4. SELECCIONAR PADRES (TORNEO k=3)                     │
└─────────────────┬───────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────┐
│  5. CREAR NUEVA POBLACIÓN                               │
│     - Copiar élites (top 5)                             │
│     - Cruzar + mutar resto                              │
└─────────────────┬───────────────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────────────┐
│  6. ¿GENERACIONES RESTANTES?                            │
│     - Sí → Volver al paso 2                             │
│     - No → Guardar resultado                            │
└─────────────────────────────────────────────────────────┘
```

---

## 4. Complejidad

### Temporal

```
TOTAL = O(G × N × L × F)

G = 1000 generaciones
N = 100 individuos
L = 750 acciones
F = 30 frames/acción

≈ 2.25 × 10⁹ operaciones
```

### Espacial

```
POBLACIÓN: 100 × 750 × 4 = 300 KB
CON PARALELIZACIÓN: ~40 MB
```

---

## 5. Librerías Utilizadas

### Algoritmo Evolutivo

| Librería | Uso |
|----------|-----|
| `random` | Selección, mutación, cruce |
| `multiprocessing` | Evaluación paralela |
| `json` | Guardar resultados |

### Simulación del Juego

| Librería | Uso |
|----------|-----|
| `pygame` | Renderizado y física |

---

## 6. Ventajas y Desventajas

### ✅ Ventajas

| Ventaja | Descripción |
|---------|-------------|
| **Simple** | No requiere math compleja |
| **Pocas dependencias** | Solo random, multiprocessing |
| **Paralelizable** | Cada individuo se evalúa independientemente |
| **Robusto** | No se estanca fácilmente |

### ⚠️ Desventajas

| Desventaja | Descripción |
|------------|-------------|
| **Lento** | Muchas evaluaciones necesarias |
| **No óptimo garantizado** | Puede encontrar óptimos locales |
| **Sin aprendizaje** | No "aprende" como RL |

---

## 7. Resultados Empíricos

### 7.1 Resultados de Entrenamiento

| Versión | Gen | Fitness | Progreso | Tiempo | Notas |
|---------|-----|---------|----------|--------|-------|
| v.1.3 | 500 | 1,242 | **33.1%** ★ | 2,288s | |
| v.1.4 | 500 | 1,868 | 28.3% | 2,959s | |
| v.1.5 | 500 | 1,277 | 19.7% | 2,978s | |
| v.1.5(f) | 500 | 1,693 | 13.8% | 2,957s | ⚠️ Fake |
| v.1.6 | 500 | 1,952 | 28.3% | 3,013s | |
| v.1.7 | 1000 | 1,688 | 17.2% | 6,275s | |
| v.1.8 | 1000 | 1,500 | 10.7% | 6,340s | |
| v.1.9 | 1000 | 2,010 | 28.3% | 6,064s | |
| v.2.1 | 1000 | 7,694 | 0.7% | 4,424s | ⚠️ Overfitting |
| v.2.1(f) | 1000 | 6,302 | 7.6% | 4,514s | ⚠️ Fake |
| v.2.2 | 1000 | 2,938 | 30.0% | 4,562s | |
| v.2.3 | 1000 | 3,529 | 28.3% | 5,299s | |
| v.2.4 | 1000 | 3,345 | 28.3% | 6,998s | ⚠️ Overfitting |
| v.2.5 | 1000 | 2,693 | 20.3% | 139s | |
| v.2.6 | 1000 | 3,884 | 28.3% | 686s | |
| v.2.7 | 1000 | **3,943** ★ | 28.3% | 2,052s | **Mejor fitness** |

### 7.2 Resultados de Evaluación

| Versión | Fitness Entrenamiento | Fitness Evaluación | Progreso Aire | Estado |
|---------|----------------------|-------------------|---------------|--------|
| v.1.9 | 2,010.0 | 2,010.0 | 28.3% (820px) | ✅ Consistente |
| v.1.9.1 | 2,010.0 | 2,010.0 | 28.3% (820px) | ✅ Consistente |
| v.2.1 | 7,694.0 | ~0.0 | 0.7% (20px) | ❌ Overfitting |
| v.2.4 | 3,345.0 | 0.0 | 28.3% (820px) | ❌ Overfitting |

---

### 7.3 Gráfica de Fitness (Entrenamiento)

```
FITNESS EN ENTRENAMIENTO
═════════════════════════════════════════════════════════════════════════════════════════

v.1.3     ██████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  1,242
v.1.4     ████████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  1,868
v.1.5     ██████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  1,277
v.1.5(f)  ██████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  1,693 ⚠️
v.1.6     █████████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  1,952
v.1.7     ██████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  1,688
v.1.8     ████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  1,500
v.1.9     ███████████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  2,010
v.1.9.1   ███████████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  2,010
v.2.1     ████████████████████████████████████████████████████████████████████████████████  7,694 ⚠️
v.2.1(f)  ███████████████████████████████████████████████████████████████████████░░░░░░  6,302 ⚠️
v.2.2     ████████████████████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░  2,938
v.2.3     ███████████████████████████████████████████████████████████░░░░░░░░░░░░░░░░░  3,529
v.2.4     █████████████████████████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░  3,345 ⚠️
v.2.5     ██████████████████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  2,693
v.2.6     ████████████████████████████████████████████████████████████████████░░░░░░░░  3,884
v.2.7     █████████████████████████████████████████████████████████████████████████░░░░  3,943 ★

          └──────────────────────────────────────────────────────────────────────────────────────────────────┘
          0              1,000              2,000              3,000              4,000              8,000
```

---

### 7.4 Gráfica de Progreso (Entrenamiento)

```
PROGRESO EN ENTRENAMIENTO (% del mapa completado)
═════════════════════════════════════════════════════════════════════════════════════════

v.1.3     ████████████████████████████████████████████████████████████████████████████████  33.1% ★ MEJOR
v.1.4     ██████████████████████████████████████████████████████████████████████░░░░░░░░░░  28.3%
v.1.5     ████████████████████████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░  19.7%
v.1.5(f)  █████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  13.8% ⚠️
v.1.6     ██████████████████████████████████████████████████████████████████████░░░░░░░░░░░  28.3%
v.1.7     █████████████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  17.2%
v.1.8     █████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  10.7%
v.1.9     ██████████████████████████████████████████████████████████████████████░░░░░░░░░░░  28.3%
v.1.9.1   ██████████████████████████████████████████████████████████████████████░░░░░░░░░░░  28.3%
v.2.1     ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   0.7% ⚠️
v.2.1(f)  ██████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   7.6% ⚠️
v.2.2     ████████████████████████████████████████████████████████████████████████░░░░░░░░░  30.0%
v.2.3     ██████████████████████████████████████████████████████████████████████░░░░░░░░░░░  28.3%
v.2.4     ██████████████████████████████████████████████████████████████████████░░░░░░░░░░░  28.3% ⚠️
v.2.5     ████████████████████████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  20.3%
v.2.6     ██████████████████████████████████████████████████████████████████████░░░░░░░░░░░  28.3%
v.2.7     ██████████████████████████████████████████████████████████████████████░░░░░░░░░░░  28.3%

          └──────────────────────────────────────────────────────────────────────────────────────────────────┘
          0%                10%               20%               30%               35%
```

---

## 8. Conclusiones

### Resumen del Algoritmo

1. **Representación:** Secuencias de acciones (0-4)
2. **Evaluación:** Simulación completa del juego
3. **Selección:** Torneo con k=3
4. **Reproducción:** Cruce de un punto + mutación
5. **Elitismo:** Top 5 sobreviven intactos
6. **Adaptación:** Mutación adaptativa según progreso

### Principales Resultados

| Métrica | Mejor Versión | Valor |
|---------|---------------|-------|
| **Mayor progreso** | v.1.3 | 33.1% |
| **Mayor fitness** | v.2.7 | 3,943 |
| **Más eficiente** | v.2.5 | 19.37 f/s |
| **Más estable** | v.1.9 | Consistente |

### Posibles Mejoras

---



