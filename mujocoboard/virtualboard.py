"""
Example of how bodies interact with each other. For a body to be able to
move it needs to have joints. In this example, the "robot" is a red ball
with X and Y slide joints (and a Z slide joint that isn't controlled).
On the floor, there's a cylinder with X and Y slide joints, so it can
be pushed around with the robot. There's also a box without joints. Since
the box doesn't have joints, it's fixed and can't be pushed around.
"""
import struct

from mujoco_py import load_model_from_path, MjSim, MjViewer
import math
import os
import numpy as np
import paho.mqtt.client as mqtt

# n time steps to apply force, x-force, y-force, z-force, x-torque, y-torque, z-torque
ROBOT_RAD = 0.15
CELL_LEN = 0.34
B_LEN = 5
B_SIZE = B_LEN ** 2
XB, YB = 3, 3
LOGIC_LEN = B_LEN * 2-1 + XB * 2
REAL_LEN = LOGIC_LEN * CELL_LEN
# how many steps the command applies external force
CMD_COOLDOWN = 250
F = 5.2
action_to_force = {
    (0,1):  [5,0,0,0, 0, F,0],
    (0,-1): [5,0,0,0, 0,-F,0],
    (1,0):  [5,0,0,0,-F, 0,0],
    (-1,0): [5,0,0,0, F, 0,0],
}

class Queue:
    def __init__(self, size):
        self.queue = [None] * size
        self.front = 0
        self.rear = 0
        self.size = size
        self.available = size

    def put(self, item):
        if self.available == 0:
            print('Queue Overflow!')
        else:
            self.queue[self.rear] = item
            self.rear = (self.rear + 1) % self.size
            self.available -= 1

    def get(self):
        if self.available == self.size:
            print('Queue Underflow!')
        else:
            item = self.queue[self.front]
            self.queue[self.front] = None
            self.front = (self.front + 1) % self.size
            self.available += 1
            return item

    def peek(self):
        return self.queue[self.front]

    def empty(self):
        return self.available==self.size


class Sphero:
    def __init__(self, xy, robot_id, model, sim):
        print('Spawning robot at', xy)
        self.y, self.x = xy
        self.r = ROBOT_RAD
        self.color = 0
        self.cmd_queue = Queue(100)
        self.robot_id = robot_id
        self.centered = False
        self.model = model
        self.sim = sim
        self.vel_integ = np.zeros(3)
        self.vel_integ_gamma = 0.5

    def getPos(self):
        return self.sim.data.body_xpos[self.robot_id]

    def center(self):
        """apply external torque to center the robot in a target cell
        proportional to velocity and distance to target
        """
        # get the current position
        pos = self.getPos()
        # get the target position
        target_x = self.x * CELL_LEN - REAL_LEN / 2
        target_y = self.y * CELL_LEN - REAL_LEN / 2
        # get the velocity
        vel = self.sim.data.body_xvelp[self.robot_id]
        self.vel_integ = self.vel_integ_gamma * (self.vel_integ + vel)
        # get the distance to target
        dist = math.sqrt((pos[0] - target_x)**2 + (pos[1] - target_y)**2)
        # check if target is reached
        if dist < 0.02 and abs(vel[0]) < 0.01 and abs(vel[1]) < 0.01:
            self.centered = True
            self.sim.data.xfrc_applied[self.robot_id] = np.zeros_like(
                self.sim.data.xfrc_applied[self.robot_id])
        else:
            self.centered = False
            # get the direction to target
            dir_x = (target_x - pos[0])
            dir_y = (target_y - pos[1])
            torque_x = 5*dir_x - 0.5* vel[0] - self.vel_integ[0]
            torque_y = 5*dir_y - 0.5* vel[1] - self.vel_integ[1]
            # apply the force
            self.sim.data.xfrc_applied[self.robot_id] = [
                0, 0, 0,
                -torque_y,
                torque_x,
                0]

    def followPath(self):
        if not self.centered:
            return False
        if self.cmd_queue.empty():
            return True
        cmd = self.cmd_queue.get()
        self.x = cmd[1]
        self.y = cmd[0]
        self.x = np.clip(self.x, 0, LOGIC_LEN-1)
        self.y = np.clip(self.y, 0, LOGIC_LEN-1)
        return False

    def setColor(self, color):
        self.color = color
        # set robot color if moving to a board
        if color == -1:
            self.model.geom_rgba[self.robot_id - 1] = (1, 1, 1, 1)
        elif color == 1:
            self.model.geom_rgba[self.robot_id - 1] = (0, 0, 0, 1)
        else:
            self.model.geom_rgba[self.robot_id - 1] = (0.5, 0.5, 0.5, 0.75)


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
        self.robots = []

        self.robot_to_id = {}
        self.coord_to_robot = -np.ones((LOGIC_LEN, LOGIC_LEN))
        for n in range(B_SIZE-1):
            self.robot_to_id[n] = self.model.body_name2id(f's{n}')
            self.robots.append(Sphero((n // LOGIC_LEN, n % LOGIC_LEN), self.robot_to_id[n], self.model, self.sim))

        self.running = True
        self.path_queue = Queue(400)
        self.running_sphero = None

    def run(self):
        initialized_pathplanning = False
        while self.running:
            self.t += 1
            new_coord_to_robot = -np.ones((LOGIC_LEN, LOGIC_LEN))
            # run robot path following
            if self.running_sphero:
                if self.running_sphero.followPath():
                    self.running_sphero = None
                    # notify the go board that the move is finished
                    # so the next move can be executed
                    self.client.publish("/boardmovedone", "", qos=2)
            else:
                if not self.path_queue.empty():
                    pathcolor = self.path_queue.get()
                    path =  pathcolor[0]
                    color = pathcolor[1]
                    # starting coordinate
                    cy, cx = path[0]
                    # if self.coord_to_robot[cy][cx] == -1
                    assert self.coord_to_robot[cy][cx] != -1, f"no robot at position {cx} {cy}"
                    sphere = self.robots[int(self.coord_to_robot[cy][cx])-1]
                    sphere.setColor(color)
                    self.running_sphero = sphere
                    for xy in path:
                        self.running_sphero.cmd_queue.put(xy)
            # center the robots and get their true positions
            for robot in self.robots:
                robot.center()
                rx, ry, _ = robot.getPos()
                x, y = round((ROBOT_RAD+rx+REAL_LEN/2) / CELL_LEN ), round((ROBOT_RAD+ry+REAL_LEN/2)/CELL_LEN)
                try:
                    new_coord_to_robot[y][x] = robot.robot_id
                except Exception as e:
                    print(f"[error] {robot.robot_id}:  {e}, {e.__traceback__}")
            # update true robot positions
            old_coord_to_robot = self.coord_to_robot
            if not np.array_equal(old_coord_to_robot, new_coord_to_robot):
                self.coord_to_robot = new_coord_to_robot
                if not initialized_pathplanning:
                    self.sendUpdatedMap(self.coord_to_robot)
                    initialized_pathplanning = True

            self.sim.step()
            self.viewer.render()
            if self.t > 100 and os.getenv('TESTING') is not None:
                break

    def sendUpdatedMap(self, map):
        occupied = (map != -1).astype(np.int32)
        self.client.publish("/gomap", occupied.tobytes())

    def handleMove(self, cli, _, tm):
        topic = tm.topic
        cmd = topic.split("/")
        if cmd[1] == "gopath":
            message = []
            for i in range(len(tm.payload)//4):
                message.append(struct.unpack('i', tm.payload[i*4:(i+1)*4])[0])
            if len(message) % 2 != 0:
                color = message[0]
                message = message[1:]
            else:
                color = 0
            coords = []
            for i in range(len(message)//2):
                coords.append((message[i*2], message[i*2+1]))
            self.path_queue.put((coords, color))


if __name__ == "__main__":
    vgb = VirtualGoBoardMQTT()
    vgb.run()