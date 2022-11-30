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
import numpy as np
import random as rnd

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

cell_len = 0.34
b_len = 5
board_size = b_len**2
x_b, y_b = 3, 3
real_len = b_len * 2 + x_b*2
# how many steps the command applies external force
CMD_DURATION = 5
n_robots = int(b_len**2)
action_to_force = {
    0: [CMD_DURATION,0,0,0,5,0,0],
    1: [CMD_DURATION,0,0,0,0,5,0],
    2: [CMD_DURATION,0,0,0,-5,0,0],
    3: [CMD_DURATION,0,0,0,0,-5,0],
}

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
        line_str_ = f"""<body name="line{i}h" pos="0 {i * 2 *cell_len + 3 * cell_len - field_size[0] / 2} 0.025">
        <geom condim="3" size="{field_size[1]} 0.02 0.02" rgba="0.2 0.2 0.2 1" type="box"/>
    </body>
    <body name="line{i}v" pos="{i * 2 * cell_len + 3 * cell_len - field_size[0] / 2} 0 0.025">
        <geom condim="3" size="0.03 {field_size[1]} 0.02" rgba="0.2 0.2 0.2 1" type="box"/>
    </body>"""
        lines_str += line_str_

    env_str = env_str.replace("LINES_", lines_str)
    return env_str

def make_random_env(n_on_board=13):
    sphero_positions = []
    # generate a robot for each player to have enough to play
    empty_spaces = [i for i in range(board_size)]
    colors = []
    # stones that are outside
    out_idx = (0, 0)
    for i in range(board_size - n_on_board):
        x = out_idx[0]
        y = out_idx[1]
        # randomly assign color
        rgba = (0.5, 0.5, 0.5, 0.75)
        colors.append(rgba)
        sphero_positions.append((x * cell_len - real_len * cell_len / 2, y * cell_len - real_len * cell_len / 2))
        nx = i % real_len
        ny = i // real_len
        out_idx = (nx, ny)
    # stones that are on the board
    for i in range(n_on_board):
        i = rnd.choice(empty_spaces)
        empty_spaces.remove(i)
        x = (i % b_len) * 2 + x_b
        y = (i // b_len) * 2 + y_b
        # randomly assign color
        rgba = (1, 1, 1, 1) if rnd.random() < 0.5 else (0, 0, 0, 1)
        colors.append(rgba)
        sphero_positions.append((x * cell_len - real_len * cell_len / 2, y * cell_len - real_len * cell_len / 2))
    env = build_env(sphero_positions, [real_len * cell_len, real_len * cell_len], colors)
    return env

def make_empty_env():
    return make_random_env(0)

class SpherosEnv(gym.Env):
    def __init__(self, obs_type="vector"):
        env_str = make_empty_env()
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
        self.robot_to_id = {}
        self.robot_to_cmd = {}
        for n in range(n_robots):
            self.robot_to_id[f's{n}'] = self.model.body_name2id(f"s{n}")
            self.robot_to_cmd[f's{n}'] = [0] * 7

        # 4 directions for each robot + 1 for no move
        self.action_space = gym.spaces.Discrete(4*n_robots + 1)

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

    def reset(self):
        self.sim.reset()
        return self.get_observations()

    def step(self, action):
        # action is a list of 4*n_robots + 1 elements
        # only apply cmd if the previous cmd finished
        robot_id = action // 4
        if robot_id < n_robots and self.robot_to_cmd[f's{robot_id}'][0] == 0:
            self.robot_to_cmd[f's{robot_id}'] = np.array(action_to_force[action % 4])
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