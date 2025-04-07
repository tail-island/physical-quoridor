from physical_quoridor import PhysicalQuoridorEnv_
from ray import tune
from ray.rllib.algorithms.ppo import PPOConfig
from ray.rllib.env.wrappers.pettingzoo_env import ParallelPettingZooEnv
from ray.tune.registry import register_env

register_env(
    "physical-quoridor",
    lambda cfg: ParallelPettingZooEnv(PhysicalQuoridorEnv_(render_mode="human")),
)

config = (
    PPOConfig()
    .environment("physical-quoridor", env_config={"n_pistons": 30})
    .api_stack(enable_rl_module_and_learner=False, enable_env_runner_and_connector_v2=False)
)

tune.run(
    "PPO",
    name="PPO",
    config=config.to_dict()
)
