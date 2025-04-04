from ray.rllib.algorithms.ppo import PPOConfig
from ray.rllib.core.rl_module.default_model_config import DefaultModelConfig
from ray.rllib.core.rl_module.multi_rl_module import MultiRLModuleSpec
from ray.rllib.core.rl_module.rl_module import RLModuleSpec
from ray.rllib.env.wrappers.pettingzoo_env import ParallelPettingZooEnv
from ray.tune import RunConfig, Tuner
from ray.tune.registry import register_env
from physical_quoridor import PhysicalQuoridorEnv


register_env("PhysicalQuoridor", lambda _: ParallelPettingZooEnv(PhysicalQuoridorEnv(render_mode="human")))

policies = {f"pursuer_{i}" for i in range(2)}

config = (
    PPOConfig().environment("PhysicalQuoridor")
)

Tuner(
    "PPO",
    run_config=RunConfig(stop={"training_iteration": 1}),
    param_space=config
).fit()
