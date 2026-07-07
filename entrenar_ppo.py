from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.monitor import Monitor
import os
from jumpking_env import JumpKingEnv


class ProgresoCallback(BaseCallback):
    def __init__(self, verbose=0):
        super().__init__(verbose)
        self.mejor_progreso = 0

    def _on_step(self):
        if self.locals["dones"][0]:
            info = self.locals["infos"][0]
            progreso = info.get("progreso", 0)
            if progreso > self.mejor_progreso:
                self.mejor_progreso = progreso
                print(f"Nuevo mejor progreso: {progreso}%")
        return True


def entrenar(total_timesteps=1000000, modelo_path="modelo_ppo"):
    print("=== Entrenamiento PPO - Jump King ===")
    print(f"Pasos totales: {total_timesteps:,}")

    env = JumpKingEnv(render_mode=None)
    env = Monitor(env)

    modelo = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        learning_rate=0.01,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.01,
        tensorboard_log="./logs/",
    )

    callback = ProgresoCallback()

    print("\nIniciando entrenamiento...")
    try:
        modelo.learn(
            total_timesteps=total_timesteps,
            callback=callback,
            progress_bar=True,
        )
    except KeyboardInterrupt:
        print("\nEntrenamiento interrumpido por el usuario.")

    modelo.save(modelo_path)
    print(f"\nModelo guardado en: {modelo_path}")

    env.close()
    return modelo


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Entrenar agente PPO para Jump King")
    parser.add_argument(
        "--timesteps", type=int, default=1000000, help="Pasos totales de entrenamiento"
    )
    parser.add_argument(
        "--model-path", type=str, default="modelo_ppo", help="Ruta para guardar el modelo"
    )
    args = parser.parse_args()

    entrenar(args.timesteps, args.model_path)
