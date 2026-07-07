from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.monitor import Monitor
import os
from jumpking_env import JumpKingEnv


class ProgresoCallback(BaseCallback):
    def __init__(self, verbose=0):
        super().__init__(verbose)
        self.mejor_progreso = 0
        self.acumulador_acciones = {
            "idle": 0,
            "left": 0,
            "right": 0,
            "charge_jump": 0,
            "jump": 0,
        }
        self.episodios_completados = 0

    def _on_step(self):
        # Acumular acciones de este paso
        info = self.locals["infos"][0]
        self.acumulador_acciones["idle"] += info.get("action_idle", 0)
        self.acumulador_acciones["left"] += info.get("action_left", 0)
        self.acumulador_acciones["right"] += info.get("action_right", 0)
        self.acumulador_acciones["charge_jump"] += info.get("action_charge_jump", 0)
        self.acumulador_acciones["jump"] += info.get("action_jump", 0)

        if self.locals["dones"][0]:
            self.episodios_completados += 1
            progreso = info.get("progreso", 0)

            # Log de progreso
            self.logger.record("episode/progreso", progreso)
            self.logger.record("episode/pasos", info.get("pasos", 0))
            self.logger.record("episode/plataformas_visitadas", info.get("plataformas_visitadas", 0))

            # Log de historial de acciones (proporción)
            total_acciones = sum(self.acumulador_acciones.values())
            if total_acciones > 0:
                for accion, count in self.acumulador_acciones.items():
                    proporcion = count / total_acciones
                    self.logger.record(f"actions/{accion}", proporcion)

            # Log de mejor progreso
            if progreso > self.mejor_progreso:
                self.mejor_progreso = progreso
                print(f"Nuevo mejor progreso: {progreso}%")

            self.logger.record("episode/mejor_progreso", self.mejor_progreso)

            # Reset acumulador
            self.acumulador_acciones = {
                "idle": 0,
                "left": 0,
                "right": 0,
                "charge_jump": 0,
                "jump": 0,
            }

        return True


def entrenar(total_timesteps=500000, modelo_path="modelo_ppo"):
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
        "--timesteps", type=int, default=500000, help="Pasos totales de entrenamiento"
    )
    parser.add_argument(
        "--model-path", type=str, default="modelo_ppo", help="Ruta para guardar el modelo"
    )
    args = parser.parse_args()

    entrenar(args.timesteps, args.model_path)
