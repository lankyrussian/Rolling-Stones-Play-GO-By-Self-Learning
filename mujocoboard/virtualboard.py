#!/usr/bin/env python3
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
command = [1, 2, 0, 0, 0,0,0]
def handleMove(cli, _, tm):
    global command
    message = tm.payload.decode("utf-8")
    topic = tm.topic
    command = [int(x) for x in message.split(',')]
    print(command)
client.on_message = handleMove
client.connect("localhost", 1883)
client.subscribe("/move")
client.loop_start()

MODEL_XML = "env.xml"

model = load_model_from_path(MODEL_XML)
sim = MjSim(model)
viewer = MjViewer(sim)
t = 0

body_id = model.body_name2id("robot")
while True:
    t += 1
    if command[0] > 0:
        sim.data.xfrc_applied[body_id] = np.array([command[1], command[2], command[3], command[4], command[5], command[6]])
        command[0] -= 1
    else:
        sim.data.xfrc_applied[body_id] = np.zeros_like(sim.data.xfrc_applied[body_id])
    sim.step()
    viewer.render()
    if t > 100 and os.getenv('TESTING') is not None:
        break