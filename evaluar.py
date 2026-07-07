from stable_baselines3 import PPO
from jumpking_env import JumpKingEnv
import time


def evaluar(modelo_path="modelo_ppo", episodes=5, velocidad=0.5):
    import pygame
    print("=== Evaluación del agente - Jump King ===")

    env = JumpKingEnv(render_mode="human")

    try:
        modelo = PPO.load(modelo_path)
        print(f"Modelo cargado desde: {modelo_path}")
    except FileNotFoundError:
        print(f"Error: No se encontró el modelo en {modelo_path}")
        print("Primero ejecuta: python entrenar_ppo.py")
        env.close()
        return

    recompensas_totales = []
    progresos = []

    for ep in range(episodes):
        obs, _ = env.reset()
        done = False
        recompensa_total = 0
        pasos = 0

        print(f"\nEpisodio {ep + 1}/{episodes}")

        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    env.close()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        env.close()
                        return

            accion, _ = modelo.predict(obs, deterministic=True)
            obs, recompensa, terminado, truncado, info = env.step(accion)
            recompensa_total += recompensa
            pasos += 1
            done = terminado or truncado

            # La ventana ya se renderiza en env.step() con render_mode="human"
            # Solo agregamos delay para visualizar
            pygame.time.Clock().tick(int(velocidad * 60))

        recompensas_totales.append(recompensa_total)
        progresos.append(info.get("progreso", 0))
        print(
            f"  Recompensa: {recompensa_total:.1f} | Progreso final: {info.get('progreso', 0)}%"
        )

        # Pausa entre episodios
        time.sleep(1)

    print(f"\n--- Resultados ---")
    print(f"Promedio recompensa: {sum(recompensas_totales) / len(recompensas_totales):.1f}")
    print(f"Promedio progreso: {sum(progresos) / len(progresos):.1f}%")
    print(f"Mejor progreso: {max(progresos)}%")

    env.close()


def jugar_manual():
    print("=== Modo manual - Jump King ===")
    print("Controles: ← → caminar | ESPACIO: cargar/soltar salto | ESC: salir")

    env = JumpKingEnv(render_mode="human")
    obs, _ = env.reset()
    import pygame

    running = True
    while running:
        accion = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            accion = 1
        elif keys[pygame.K_RIGHT]:
            accion = 2
        elif keys[pygame.K_SPACE]:
            accion = 3

        obs, recompensa, terminado, truncado, info = env.step(accion)

        env.ventana.fill((0, 0, 20))
        env.mapa.dibujar(env.ventana, env.camara_y)
        env.jugador.dibujar(env.ventana, env.camara_y)

        font = pygame.font.SysFont(None, 30)
        progreso = info.get("progreso", 0)
        texto = font.render(f"Progreso: {progreso}%", True, (255, 255, 255))
        env.ventana.blit(texto, (10, 10))

        pygame.display.update()

        if terminado:
            print("Meta alcanzada!")
            time.sleep(2)
            obs, _ = env.reset()
        elif truncado:
            print("Límite de pasos alcanzado")
            obs, _ = env.reset()

    env.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Evaluar agente Jump King")
    parser.add_argument(
        "--model-path", type=str, default="modelo_ppo", help="Ruta del modelo"
    )
    parser.add_argument(
        "--episodes", type=int, default=5, help="Número de episodios"
    )
    parser.add_argument(
        "--speed", type=float, default=0.5, help="Velocidad de visualización"
    )
    parser.add_argument(
        "--manual", action="store_true", help="Jugar manualmente"
    )
    args = parser.parse_args()

    if args.manual:
        jugar_manual()
    else:
        evaluar(args.model_path, args.episodes, args.speed)
