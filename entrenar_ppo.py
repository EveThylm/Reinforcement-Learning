from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.monitor import Monitor
from jumpking_env import JumpKingEnv


class ProgresoCallback(BaseCallback):
    def __init__(self, verbose=0):
        super().__init__(verbose)
        self.mejor_progreso = 0

    def _on_step(self):
        if self.locals["dones"][0]:
            info = self.locals["infos"][0]
            progreso = info.get("progreso", 0)
            plats = info.get("plataformas_visitadas", 0)
            altura = info.get("altura_maxima", 0)

            if progreso > self.mejor_progreso:
                self.mejor_progreso = progreso
                print(f"Nuevo mejor: {progreso}% | Plataformas: {plats} | Altura: {altura:.0f}")

            self.logger.record("progreso", progreso)
            self.logger.record("plataformas", plats)
            self.logger.record("mejor_progreso", self.mejor_progreso)

        return True


def entrenar(total_timesteps=100000, modelo_path="modelo_ppo"):
    print(f"=== Entrenamiento PPO | {total_timesteps:,} pasos ===")

    env = JumpKingEnv(render_mode=None)
    env = Monitor(env)

    modelo = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        learning_rate=0.0005,
        n_steps=1024,
        batch_size=128,
        n_epochs=10,
        gamma=0.995,
        ent_coef=0.1,
        tensorboard_log="./logs/",
    )

    callback = ProgresoCallback()

    try:
        modelo.learn(total_timesteps=total_timesteps, callback=callback, progress_bar=True)
    except KeyboardInterrupt:
        print("\nInterrumpido.")

    modelo.save(modelo_path)
    print(f"Modelo guardado: {modelo_path}")
    env.close()
    return modelo


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--timesteps", type=int, default=200000)
    parser.add_argument("--model-path", type=str, default="modelo_ppo")
    args = parser.parse_args()
    entrenar(args.timesteps, args.model_path)
