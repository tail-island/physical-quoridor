import os

from pyarrow.fs import LocalFileSystem
from random import Random
from ray import init
from ray.rllib.algorithms.ppo import PPOConfig
from ray.rllib.core.rl_module.default_model_config import DefaultModelConfig
from ray.rllib.core.rl_module.multi_rl_module import MultiRLModuleSpec
from ray.rllib.core.rl_module.rl_module import RLModuleSpec
from ray.rllib.env.wrappers.pettingzoo_env import ParallelPettingZooEnv
from ray.tune.registry import register_env
from env import PhysicalQuoridorEnv_


rng = Random(1234)

init()

register_env(
    "physical_quoridor",
    lambda _: ParallelPettingZooEnv(PhysicalQuoridorEnv_()),
    # lambda _: ParallelPettingZooEnv(PhysicalQuoridorEnv_(render_mode="human")),  # こちらにすると、学習中のプレイが見えて面白いです。
)

config = (
    PPOConfig()
    .environment("physical_quoridor")
    .multi_agent(
        policies={"policy_0", "policy_1"},
        policy_mapping_fn=lambda agent, episode, **kwargs: rng.choice(["policy_0", "policy_1"]),
        algorithm_config_overrides_per_module={
            "policy_0": PPOConfig.overrides(gamma=0.95),
            "policy_1": PPOConfig.overrides(gamma=0.9)
        }
    )
    .rl_module(rl_module_spec=MultiRLModuleSpec(rl_module_specs={
        "policy_0": RLModuleSpec(
            model_config=DefaultModelConfig(
                fcnet_hiddens=[512, 512, 512, 512],
                fcnet_activation="relu"
            )
        ),
        "policy_1": RLModuleSpec(
            model_config=DefaultModelConfig(
                fcnet_hiddens=[512, 512, 512, 512],
                fcnet_activation="relu"
            )
        )
    }))
    .env_runners(num_env_runners=8)
)

algo = config.build_algo()

for i in range(1_000_000):
    algo.train()

    if (i + 1) % 100 == 0:
        checkpoint_path = f"./checkpoints/{i + 1:06}"

        os.makedirs(checkpoint_path, exist_ok=True)
        algo.save_to_path(checkpoint_path, filesystem=LocalFileSystem())
