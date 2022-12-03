#!/bin/sh
mosquitto -d && xhost local:root && /rspg/pathplanning/PathPlanner & \
cd /rspg/mujocoboard ; python3 virtualboard.py & cd /rspg/goboard/src ; python3 playgo.py