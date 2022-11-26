import gym
import envs

env = gym.make('Spheros-v0')

env.configure(obs_type="vector")
env.reset()

for _ in range(1000):
    env.render("human")
    obs = env.step(env.action_space.sample())