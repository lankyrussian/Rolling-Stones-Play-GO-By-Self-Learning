Using Sphero robots to play Go.

## Running the game

Use [the rspg docker image](https://hub.docker.com/repository/docker/ymyrvolod/rspg) if you are using linux with X11 display manager.
This will start the game against the pre-trained alphazero model:   
`docker run -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=$DISPLAY -h $HOSTNAME -it rspg`   
Switch back to the terminal after you see the simulator window appear, enter stone coordinates separated by space.

Alternatively, setup each individual component as described below.
After the setup, start the pathplanner, goboard, then the mujoco simulator.

## goboard

go game engine implementation of the interface from [alpha-zero-general](https://github.com/suragnair/alpha-zero-general).
current features:
* play go against a random agent
* send mqtt commands about stone placement to pathfinding
* train AlphaZero
* play against AlphaZero

### setup

If using Nvidia GPU:   
[install conda for linux](https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html)   
`conda create --name rlpg --file env.txt`

### run
`python src/playgo.py` - against latest trained agent. Pre-trained agent has to be located in `./src/pretrained/`    
`python src/playgo.py --player2 r` - against random agent   
`python src/playgo.py --player2 h` - against another player    
`python src/playgo.py --player1 a --player2 a` - watch ai against ai

### test
 
`python -m unittest test/GoGameTests.py`

## pathfinding

A* pathfinding for the expanded go grid. The logical grid is expanded to include a
unit of space between all robots for simpler pathfinding.    
Features:
* A* pathfinding for putting new stones on the board, and removing stones from the board
* reads the initial board state published by the mujocoboard
* publishes path commands to the mujocoboard 

### setup
install mosquitto:    
`sudo apt-get install libmosquitto-dev mosquitto-dev`    
`cd pathplanning ; make`

### run   
`./PathPlanner`

## mujocoboard

virtual board to simulate sphero movement on path commands

### setup

[Install Mujoco](https://blog.guptanitish.com/blog/install-mujoco/).   
If using conda, make a soft link from the local `/usr/lib/x86_64-linux-gnu/libstdc++.so.6` to
the corresponding file in your conda env.

make sure the LD_PRELOAD env variable is setup to render mujoco:     
`export LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libGLEW.so`

### run
(optional) make a go virtual board environment xml with a initial stone placement:    
`python make_env.py`   

run the mujoco simulation using board.xml:    
`python virtualboard.py`

### Using Repositories

[alpha-zero-general](https://github.com/suragnair/alpha-zero-general)   
