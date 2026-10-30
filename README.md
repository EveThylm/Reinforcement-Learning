# Jumpikingo — Jump King AI

A recreation of the platformer **Jump King** built with Pygame, plus two AI approaches that try to beat it:

- **Evolutionary algorithm** (`evolutivo.py`) — evolves a sequence of jump actions to climb as high as possible. Self-contained: only needs Pygame.
- **Reinforcement learning** (`Trainning vs evaluation/`) — a Gymnasium / Stable-Baselines3 environment and training/evaluation pipeline.

The game is played by charging and releasing jumps: hold <kbd>Space</kbd> to charge, release to jump. Left/Right steer while airborne. Falling all the way back down is part of the pain.

## Project structure

```
├── main.py              # Play the game manually (Pygame window)
├── evolutivo.py         # Evolutionary algorithm — finds the best action sequence
├── evaluar_gen.py       # Replay/evaluate the best saved sequence
├── fitness.py           # Fitness function (height, waypoints, penalties)
├── audit_mapa.py        # Map analysis tool
├── personaje.py         # Player character (physics, charging, animations)
├── mapa.py              # Map construction and waypoints
├── nivel.py             # Level definition
├── plataforma.py        # Platform class
├── constantes.py        # Game/algorithm constants
├── mejor_secuencia.txt  # Best sequence found so far
├── Trainning vs evaluation/   # RL environment + per-version experiment logs
├── Knight_player/       # Knight sprite assets
├── assets/              # Backgrounds and player sprites
└── *.md                 # Design docs and experiment reports (Spanish)
```

## Installation

Requires Python 3.10+.

```bash
pip install -r requirements.txt
```

The evolutionary algorithm only needs `pygame`:

```bash
pip install pygame-ce
```

## Usage

### Play manually

```bash
python main.py
```

Controls: <kbd>←</kbd>/<kbd>→</kbd> move, <kbd>Space</kbd> charge & release to jump, <kbd>R</kbd> reset.

### Run the evolutionary algorithm

```bash
python evolutivo.py --generaciones 1000 --poblacion 100 --acciones 750 --paralelo
```

| Flag | Default | Description |
|------|---------|-------------|
| `--generaciones` | 1000 | Number of generations |
| `--poblacion` | 100 | Population size |
| `--acciones` | 750 | Actions per sequence |
| `--mutacion` | 0.3 | Base mutation rate |
| `--elites` | 5 | Elite individuals carried unchanged |
| `--padres` | 10 | Tournament winners used for breeding |
| `--paralelo` | off | Evaluate individuals in parallel (multiprocessing) |

The best sequence is saved to `mejor_secuencia.txt`.

### Replay the best sequence

```bash
python evaluar_gen.py --velocidad 0.5 --repeticiones 1 --frames 30
```

## How the evolutionary algorithm works

Each individual is a sequence of actions from `{0 idle, 1 high-left, 2 high-right, 3 low-left, 4 low-right}`. Every generation:

1. **Evaluate** — simulate the full game for each sequence and score it with `fitness.py`:
   `fitness = ground_height + 0.5·air_height + 200·waypoints − fall/idle/stuck penalties`
2. **Select** — tournament selection (k=3).
3. **Reproduce** — one-point crossover and per-gene / segment mutation.
4. **Adapt** — mutation rate decreases on improvement, increases when stalled; every 20 stagnant generations, 10% of the population is replaced with random individuals.
5. **Elitism** — the top 5 survive unchanged, so fitness never regresses.

For a full breakdown (with diagrams), see [`Proyecto_evolutivo.md`](Proyecto_evolutivo.md).

## Experiment results

Empirical results across versions are logged in [`Trainning vs evaluation/`](Trainning%20vs%20evaluation/) and summarized in [`Proyecto_evolutivo.md`](Proyecto_evolutivo.md#9-resultados-empíricos). Highlights:

- **Best absolute fitness:** v.2.7 — 3,943 (820px climbed, 28.3% of map)
- **Best relative progress:** v.1.3 — 33.1%
- **Most efficient:** v.2.5 — 19.37 fitness/second

A known issue: some 2.x versions score high in training but ~0 in evaluation (overfitting to the sequence replay rather than generalizing).

## Documentation (Spanish)

- [`# Proyecto Recreación de Jump King.md`](%23%20Proyecto%20Recreaci%C3%B3n%20de%20Jump%20King.md) — game recreation design
- [`# Diseño del Agente de Reinforcemen.md`](%23%20Dise%C3%B1o%20del%20Agente%20de%20Reinforcemen.md) — RL agent design
- [`Proyecto_evolutivo.md`](Proyecto_evolutivo.md) — evolutionary algorithm deep-dive
- [`Presentacion_JumpKing.md`](Presentacion_JumpKing.md) — presentation

## Credits

Player and knight sprites from free asset packs (see `Knight_player/Read_me.txt`).
