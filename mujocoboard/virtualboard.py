"""
Example of how bodies interact with each other. For a body to be able to
move it needs to have joints. In this example, the "robot" is a red ball
with X and Y slide joints (and a Z slide joint that isn't controlled).
On the floor, there's a cylinder with X and Y slide joints, so it can
be pushed around with the robot. There's also a box without joints. Since
the box doesn't have joints, it's fixed and can't be pushed around.
"""
from mujoco_py import load_model_from_path, MjSim, MjViewer
import math
import os
import numpy as np
import paho.mqtt.client as mqtt

client = mqtt.Client()
# n time steps to apply force, x-force, y-force, z-force, x-torque, y-torque, z-torque
robot_to_cmd = {}
# how many steps the command applies external force
CMD_DURATION = 5
action_to_force = {
    0: [CMD_DURATION,0,0,0,5,0,0],
    1: [CMD_DURATION,0,0,0,0,5,0],
    2: [CMD_DURATION,0,0,0,-5,0,0],
    3: [CMD_DURATION,0,0,0,0,-5,0],
}
# path level coordinate to robot
coord_to_robot = {}
N_ROBOTS = 24
cell_len = 0.34

def handleMove(cli, _, tm):
    global robot_to_cmd
    topic = tm.topic
    cmd = topic.split("/")
    if cmd[1] == "robotmove":
        message = tm.payload.decode("utf-8")
        robot_to_cmd[cmd[-1]] = [int(x) for x in message.split(',')]
    elif cmd[1] == "gopath":
        message = []
        for i in range(len(tm.payload)//4):
            tempBytes = tm.payload[(i*4):((i*4)+4)]
            message.append(int.from_bytes(tempBytes, "little"))

client.on_message = handleMove
client.connect("localhost", 1883)
client.subscribe("/robotmove/#")
client.subscribe("/gopath")
client.loop_start()

MODEL_XML = "board.xml"

model = load_model_from_path(MODEL_XML)
sim = MjSim(model)
viewer = MjViewer(sim)
t = 0

robot_to_id = {}
for n in range(N_ROBOTS):
    robot_to_id[n] = model.body_name2id(n)
    robot_to_cmd[n] = [0, 0, 0, 0, 0, 0, 0]
    rx, ry, _ = sim.data.body_xpos[robot_to_id[n]]
    x, y = int(rx/cell_len), int(ry/cell_len)
    coord_to_robot = np.zeros((5,5))
    coord_to_robot[y][x] = n

while True:
    t += 1
    for robot, cmd in robot_to_cmd.items():
        if cmd[0] > 0:
            cmd[0] -= 1
            sim.data.xfrc_applied[robot_to_id[robot]] = np.array(cmd[1:])
        else:
            sim.data.xfrc_applied[robot_to_id[robot]] = np.zeros_like(sim.data.xfrc_applied[robot_to_id[robot]])
        rx, ry, _ = sim.data.body_xpos[robot_to_id[robot]]
        x, y = int(rx / cell_len), int(ry / cell_len)
        coord_to_robot = np.zeros((5, 5))
        coord_to_robot[y][x] = robot
    sim.step()
    viewer.render()
    if t > 100 and os.getenv('TESTING') is not None:
        break