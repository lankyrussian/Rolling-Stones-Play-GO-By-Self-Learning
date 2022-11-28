#!/usr/bin/env python3
"""
Example of how bodies interact with each other. For a body to be able to
move it needs to have joints. In this example, the "robot" is a red ball
with X and Y slide joints (and a Z slide joint that isn't controlled).
On the floor, there's a cylinder with X and Y slide joints, so it can
be pushed around with the robot. There's also a box without joints. Since
the box doesn't have joints, it's fixed and can't be pushed around.
"""
import math

import gym
from mujoco_py import load_model_from_xml, MjSim, MjViewer, MjRenderContextOffscreen
import os
import numpy as np

MODEL_XML = """<?xml version="1.0" ?>
<mujoco>
    <option timestep="0.005" />
    <worldbody>
        <camera euler="0 0 0" fovy="40" name="rgb" pos="0 0 2.5"></camera>
        SPHEROS_
        <body name="floor" pos="FLOOR_ 0.025">
            <geom condim="3" size="FLOORSIZE_ 0.02" rgba="0.8 0.8 0.8 1" type="box"/>
        </body>
        LINES_
    </worldbody>
</mujoco>
"""

class SpherosEnv(gym.Env):
    def __init__(self, sphero_positions=[(0, 0), (0.3, 0), (0.6, 0), (0.8, 0), (1.0, 0)], field_size=[10, 10], obs_type="vector"):
        env_str = SpherosEnv.build_env(sphero_positions, field_size)
        self.model = load_model_from_xml(env_str)
        self.sim = MjSim(self.model)
        self.obs_type = obs_type
        if obs_type == "image":
            self.get_observations = self._get_observations_img
        elif obs_type == "vector":
            self.get_observations = self._get_observations_vector
        else:
            raise ValueError("obs_type must be 'image' or 'vector'")
        self.offviewer = MjRenderContextOffscreen(self.sim, 0)
        self.viewer = MjViewer(self.sim)
        t = 0
        self.robot_to_id = {}
        self.robot_to_cmd = {}
        for n in range(len(sphero_positions)):
            self.robot_to_id[f's{n}'] = self.model.body_name2id(f"s{n}")
            self.robot_to_cmd[f's{n}'] = [0] * len(sphero_positions)

        self.action_space = gym.spaces.Box(low=-1, high=1, shape=(len(sphero_positions), 3), dtype=np.float32)

    def configure(self, **kwargs):
        self.__init__(**kwargs)

    def get_observations(self):
        raise NotImplementedError()

    def _get_observations_vector(self):
        qpos = self.sim.data.qpos
        qvel = self.sim.data.qvel
        return np.concatenate([qpos.flat, qvel.flat])

    def _get_observations_img(self):
        self.offviewer.render(420, 380, 0)
        data = np.asarray(self.offviewer.read_pixels(420, 380, depth=False)[::-1, :, :], dtype=np.uint8)
        return data

    @staticmethod
    def build_env(sphero_poss, field_size, colors=None):
        env_str = MODEL_XML
        spheros_str = ""
        if colors:
            assert len(colors) == len(sphero_poss)
        for si, pos in enumerate(sphero_poss):
            rgba = " ".join([str(i) for i in colors[si]]) if colors else "0.5 0.5 0.5 0.75"
            sphero_str = f"""
        <body name="s{si}" pos="{pos[0]} {pos[1]} 0.4">
            <joint type="free" stiffness="0" damping="0" frictionloss="0.1" armature="0"/>
            <geom mass="1.0" friction="1 1 1" pos="0 0 0" rgba="{rgba}" size="0.15" type="sphere"/>
        </body>"""
            spheros_str += sphero_str
        env_str = env_str.replace("SPHEROS_", spheros_str)
        floor_coords_str = "0 0"  # f"{-field_size[0]/2} {-field_size[1]/2}"
        env_str = env_str.replace("FLOOR_", floor_coords_str)
        env_str = env_str.replace("FLOORSIZE_", f"{field_size[0]} {field_size[1]}")
        # add board vertical and horizontal lines
        lines_str = ""
        n_rows = int(math.sqrt(len(sphero_poss)))
        for i in range(0, n_rows):
            line_str_ = f"""<body name="line{i}h" pos="0 {i*2*0.33 + 3*0.33 -field_size[0]/2} 0.025">
            <geom condim="3" size="{field_size[1]} 0.02 0.02" rgba="0.2 0.2 0.2 1" type="box"/>
        </body>
        <body name="line{i}v" pos="{i*2*0.33 + 3*0.33 -field_size[0]/2} 0 0.025">
            <geom condim="3" size="0.03 {field_size[1]} 0.02" rgba="0.2 0.2 0.2 1" type="box"/>
        </body>"""
            lines_str += line_str_

        env_str = env_str.replace("LINES_", lines_str)
        return env_str

    def reset(self):
        self.sim.reset()
        return self.get_observations()

    def step(self, action):
        # todo: define meaningful actions that would output valid torques for the spheros
        for robot, cmd in self.robot_to_cmd.items():
            if cmd[0] > 0:
                cmd[0] -= 1
                self.sim.data.xfrc_applied[self.robot_to_id[robot]] = np.array(cmd[1:])
            else:
                self.sim.data.xfrc_applied[self.robot_to_id[robot]] = \
                    np.zeros_like(self.sim.data.xfrc_applied[self.robot_to_id[robot]])

        self.sim.step()
        return self.get_observations(), 0, False, {}

    def render(self, mode='human'):
        if mode == 'human':
            self.viewer.render()
        elif mode == 'rgb_array':
            # don't need to redraw if the image was already to rendered in step()
            if not self.obs_type == "image":
                self.offviewer.render(420, 380, 0)
            data = np.asarray(self.offviewer.read_pixels(420, 380, depth=False)[::-1, :, :], dtype=np.uint8)
            return data