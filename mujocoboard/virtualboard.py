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
from queue import Queue


# n time steps to apply force, x-force, y-force, z-force, x-torque, y-torque, z-torque
robot_to_cmd = {}
ROBOT_RAD = 0.15
CELL_LEN = 0.34
B_LEN = 5
B_SIZE = B_LEN ** 2
XB, YB = 3, 3
LOGIC_LEN = B_LEN * 2-1 + XB * 2
REAL_LEN = LOGIC_LEN * CELL_LEN
# how many steps the command applies external force
CMD_DURATION = 5
action_to_force = {
    (0,1): [CMD_DURATION,0,0,0,5,0,0],
    (0,-1): [CMD_DURATION,0,0,0,0,5,0],
    (1,0): [CMD_DURATION,0,0,0,-5,0,0],
    (-1,0): [CMD_DURATION,0,0,0,0,-5,0],
}

class VirtualGoBoardMQTT:
    def __init__(self):
        client = mqtt.Client()
        client.on_message = self.handleMove
        client.connect("localhost", 1883)
        client.subscribe("/robotmove/#")
        client.subscribe("/gopath")
        client.loop_start()
        self.client = client

        MODEL_XML = "board.xml"

        self.model = load_model_from_path(MODEL_XML)
        self.sim = MjSim(self.model)
        self.viewer = MjViewer(self.sim)
        self.t = 0
        # path level coordinate to robot
        self.coord_to_robot = {}

        self.robot_to_id = {}
        self.coord_to_robot = -np.ones((LOGIC_LEN, LOGIC_LEN))
        for n in range(B_SIZE-1):
            self.robot_to_id[n] = self.model.body_name2id(f's{n}')
            robot_to_cmd[n] = Queue()

        self.running = True

    def run(self):
        while self.running:
            self.t += 1
            # reset robot coordinates
            old_coord_to_robot = self.coord_to_robot
            self.coord_to_robot = -np.ones((LOGIC_LEN, LOGIC_LEN))
            for robot, cmdq in robot_to_cmd.items():
                if not cmdq.empty():
                    cmd = cmdq.peek()
                    if cmd[0] == 0:
                        cmdq.get()
                    else:
                        cmd[0] -= 1
                    self.sim.data.xfrc_applied[self.robot_to_id[robot]] = np.array(cmd[1:])
                else:
                    self.sim.data.xfrc_applied[self.robot_to_id[robot]] = np.zeros_like(
                        self.sim.data.xfrc_applied[self.robot_to_id[robot]])
                rx, ry, _ = self.sim.data.body_xpos[self.robot_to_id[robot]]
                x, y = round((ROBOT_RAD+rx+REAL_LEN/2) / CELL_LEN ), round((ROBOT_RAD+ry+REAL_LEN/2)/CELL_LEN)
                try:
                    self.coord_to_robot[y][x] = robot
                except:
                    print(f"error, robot out of bounds: {robot}, {x}, {y}")
            if not np.array_equal(old_coord_to_robot, self.coord_to_robot):
                print(self.coord_to_robot)
                self.sendUpdatedMap(self.coord_to_robot)

            self.sim.step()
            self.viewer.render()
            if self.t > 100 and os.getenv('TESTING') is not None:
                break

    def sendUpdatedMap(self, map):
        occupied = (map != -1).astype(np.int32)
        print(occupied.sum())
        self.client.publish("/gomap", occupied.tobytes())

    def moveStone(self, path, color):
        # set robot color if moving to a board
        if color == 1:
            self.model.geom_rgba[color] = (1, 1, 1, 1)
        elif color == -1:
            self.model.geom_rgba[color] = (0, 0, 0, 1)
        else:
            self.model.geom_rgba[color] = (0.5, 0.5, 0.5, 0.75)
        # check that the robot is present at the start of the path
        cx, cy = path[0]
        assert self.coord_to_robot[(cx, cy)] != -1, f"no robot at position {cx} {cy}"
        while len(path)>1:
            # current position
            cx, cy = path[0]
            # next position
            nx, ny = path[1]
            assert self.coord_to_robot[(nx, ny)] == -1, f"position {nx} {ny} is occupied"
            action = (nx - cx, ny - cy)
            robot = self.coord_to_robot[(cx, cy)]
            robot_to_cmd[robot].put(np.array(action_to_force[action]))
            path = path[1:]

    def handleMove(self, cli, _, tm):
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
            color = message[0]
            coords = []
            for i in range(len(message)//2):
                coords.append((message[i*2+1], message[i*2+1+1]))
            self.moveStone(coords, color)


if __name__ == "__main__":
    vgb = VirtualGoBoardMQTT()
    vgb.run()