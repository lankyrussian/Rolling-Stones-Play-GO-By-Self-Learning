from gym.envs.registration import register


register(
    id="Spheros-v0",
    entry_point="mujocoboard.envs.virtualboard:SpherosEnv",
    max_episode_steps=20000,
)