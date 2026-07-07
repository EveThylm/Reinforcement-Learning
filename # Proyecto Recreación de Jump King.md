# Proyecto: Recreación de Jump King en Python

## Descripción General

Desarrollar una recreación de los primeros niveles de **Jump King (2019)** utilizando:

* Python 3.14
* Pygame-CE

El objetivo principal es reproducir las mecánicas fundamentales del juego, especialmente el sistema de salto cargado, las colisiones, la gravedad y la navegación entre pantallas.

---

# Objetivos del Proyecto

## Objetivo General

Crear una versión funcional de los primeros niveles de Jump King que permita:

* Controlar un personaje.
* Cargar y ejecutar saltos.
* Interactuar con plataformas mediante colisiones.
* Ascender y descender entre pantallas.
* Construir niveles mediante un sistema de mapas reutilizable.

---

# Alcance Inicial (MVP)

La primera versión debe permitir:

```text
Jugador
↓
Salta
↓
Colisiona con plataformas
↓
Puede caer
↓
Puede cambiar de pantalla
```

No es necesario implementar inicialmente:

* Animaciones avanzadas.
* Menús.
* Efectos de sonido.
* Guardado de partida.
* Sistema de logros.

---

# Requisitos Funcionales

## RF-1: Personaje Jugable

El jugador debe poseer:

* Posición horizontal (x)
* Posición vertical (y)
* Ancho
* Alto

### Datos mínimos

```text
Jugador
├─ x
├─ y
├─ ancho
└─ alto
```

---

## RF-2: Sistema de Gravedad

El personaje debe verse afectado por una aceleración constante hacia abajo.

### Comportamiento esperado

```text
Si no existe una plataforma debajo
    ↓
La velocidad vertical aumenta
    ↓
El personaje cae
```

### Características

* Gravedad constante.
* Velocidad máxima de caída configurable.
* Detección de aterrizaje.

---

## RF-3: Mecánica de Salto Estilo Jump King

### Comportamiento

```text
Mantener tecla presionada
↓
Acumular fuerza
↓
Soltar tecla
↓
Ejecutar salto
```

### Restricciones

* No existe doble salto.
* No existe control aéreo significativo.
* La dirección del salto se define antes de despegar.
* La potencia depende del tiempo de carga.

### Variables necesarias

```text
fuerza_salto
tiempo_carga
direccion
```

---

## RF-4: Sistema de Colisiones

El personaje no debe atravesar:

* Suelo
* Plataformas
* Muros

### Colisiones requeridas

```text
arriba
abajo
izquierda
derecha
```

### Funcionalidades

* Detectar aterrizajes.
* Detectar golpes contra techos.
* Detectar colisiones laterales.
* Evitar atravesar objetos sólidos.

---

## RF-5: Sistema de Plataformas

Las plataformas deben:

* Tener posición.
* Tener tamaño.
* Ser sólidas.

### Estructura conceptual

```text
Plataforma
├─ x
├─ y
├─ ancho
└─ alto
```

---

## RF-6: Sistema de Mapas

Los niveles deben poder construirse sin modificar la lógica del juego.

### Ejemplo conceptual

```text
Nivel
├─ Plataforma 1
├─ Plataforma 2
├─ Plataforma 3
└─ Plataforma N
```

### Requisitos

* Fácil creación de nuevas pantallas.
* Posibilidad de reutilizar componentes.
* Separación entre lógica y contenido.

---

## RF-7: Transición entre Pantallas

### Subida

```text
Pantalla 1
     ↑
Jugador
     ↑
Pantalla 2
```

Cuando el jugador alcanza el límite superior:

* Se carga la pantalla superior.

### Bajada

```text
Pantalla 2
     ↓
Jugador
     ↓
Pantalla 1
```

Cuando el jugador cae:

* Se carga la pantalla inferior.

---

## RF-8: Cámara

La cámara debe:

* Mostrar únicamente la pantalla actual.
* Mantener visible el nivel correspondiente.
* Permitir transiciones entre áreas.

---

# Requisitos No Funcionales

## RNF-1: Programación Orientada a Objetos

El proyecto debe utilizar clases.

### Clases mínimas recomendadas

```text
Juego
Jugador
Plataforma
Nivel
```

---

## RNF-2: Organización Modular

### Estructura sugerida

```text
proyecto/

├─ main.py
├─ constantes.py
├─ jugador.py
├─ plataforma.py
├─ nivel.py
└─ juego.py
```

---

## RNF-3: Rendimiento

Objetivo:

```text
60 FPS
```

Uso recomendado:

```python
clock.tick(60)
```

---

## RNF-4: Mantenibilidad

El código debe:

* Ser legible.
* Tener responsabilidades separadas.
* Facilitar la creación de nuevos niveles.

---

# Arquitectura Inicial

```text
Juego
│
├── Jugador
│
├── Nivel Actual
│      │
│      ├── Plataforma
│      ├── Plataforma
│      └── Plataforma
│
└── Cámara
```

---

# Modelo de Clases Inicial

## Juego

Responsabilidades:

* Ejecutar el bucle principal.
* Actualizar entidades.
* Dibujar elementos.
* Gestionar niveles.

---

## Jugador

Responsabilidades:

* Movimiento.
* Gravedad.
* Salto.
* Colisiones.

### Atributos principales

```text
x
y
velocidad_x
velocidad_y
fuerza_salto
en_suelo
```

---

## Plataforma

Responsabilidades:

* Representar superficies sólidas.

### Atributos principales

```text
x
y
ancho
alto
```

---

## Nivel

Responsabilidades:

* Almacenar plataformas.
* Gestionar transiciones.

### Atributos principales

```text
id
plataformas
nivel_superior
nivel_inferior
```

---

# Plan de Desarrollo

## Fase 1: Ventana

### Objetivos

* Crear ventana.
* Dibujar jugador.

### Resultado esperado

```text
✓ Ventana visible
✓ Rectángulo visible
```

---

## Fase 2: Movimiento Básico

### Objetivos

* Movimiento horizontal.

### Resultado esperado

```text
✓ Izquierda
✓ Derecha
```

---

## Fase 3: Gravedad

### Objetivos

* Aplicar aceleración vertical.

### Resultado esperado

```text
✓ Caída continua
```

---

## Fase 4: Plataformas

### Objetivos

* Detectar colisiones.

### Resultado esperado

```text
✓ El jugador aterriza
✓ No atraviesa el suelo
```

---

## Fase 5: Salto Básico

### Objetivos

* Saltar desde una plataforma.

### Resultado esperado

```text
✓ Salto funcional
```

---

## Fase 6: Salto Estilo Jump King

### Objetivos

* Implementar carga de salto.

### Resultado esperado

```text
✓ Mantener para cargar
✓ Soltar para ejecutar
✓ Distintas alturas
```

---

## Fase 7: Sistema de Niveles

### Objetivos

* Crear múltiples pantallas.

### Resultado esperado

```text
✓ Niveles independientes
✓ Fácil edición
```

---

## Fase 8: Transiciones

### Objetivos

* Cambiar entre pantallas.

### Resultado esperado

```text
✓ Subir de pantalla
✓ Bajar de pantalla
```

---

# Prioridades del Proyecto

## Prioridad Alta

* Movimiento
* Gravedad
* Colisiones
* Salto cargado

## Prioridad Media

* Sistema de niveles
* Transiciones

## Prioridad Baja

* Gráficos
* Animaciones
* Sonido

---

# Estrategia Recomendada

Desarrollar primero con figuras simples:

```text
Jugador      → Rectángulo
Plataformas  → Rectángulos
Nivel        → Bloques básicos
```

Una vez que la física y el salto funcionen correctamente:

```text
1. Sprites
2. Animaciones
3. Sonidos
4. Interfaz
```

La mecánica de salto debe ser la máxima prioridad, ya que constituye el núcleo de la experiencia de juego de Jump King.
