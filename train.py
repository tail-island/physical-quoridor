from physical_quoridor import PhysicalQuoridorEnv_
from pprint import pprint
from ray import init
from ray.rllib.algorithms.ppo import PPOConfig
from ray.rllib.core.rl_module.default_model_config import DefaultModelConfig
from ray.rllib.core.rl_module.multi_rl_module import MultiRLModuleSpec
from ray.rllib.core.rl_module.rl_module import RLModuleSpec
from ray.rllib.env.wrappers.pettingzoo_env import ParallelPettingZooEnv
from ray.tune.registry import register_env

init()

register_env(
    "physical-quoridor",
    lambda cfg: ParallelPettingZooEnv(PhysicalQuoridorEnv_(render_mode="human")),
)

config = (
    PPOConfig()
    .environment("physical-quoridor", env_config={"n_pistons": 30})
    .multi_agent(
        policies={"0", "1"},
        policy_mapping_fn=lambda agent, episode, **kwargs: str(agent)
    )
    .rl_module(rl_module_spec=MultiRLModuleSpec(rl_module_specs={
        "0": RLModuleSpec(
            model_config=DefaultModelConfig(
                fcnet_hiddens=[128, 256, 512, 256, 128]
            )
        ),
        "1": RLModuleSpec()
    }))
    .env_runners(num_env_runners=2)
)

algo = config.build_algo()

for _ in range(1_000):
    pprint(algo.train())
    print()
