Using Sphero robots to play Go.

## goboard

go game engine implementation of the interface from [alpha-zero-general](https://github.com/suragnair/alpha-zero-general).
current features:
* play go against a random agent
* send mqtt commands about stone placement to pathfinding

### Setup

[install conda for linux](https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html)   
`conda create --name rlpg --file env.txt`

### Play against a random agent

`python src/playgo.py`

### Test
 
`python -m unittest test/GoGameTests.py`

## pathfinding

A* pathfinding for the expanded go grid. The logical grid is expanded to include a
unit of space between all robots for simpler pathfinding.
Features:
* A* pathfinding for putting new stones on the board, and removing stones from the board

### setup
install mosquitto:    
`sudo apt-get install libmosquitto-dev mosquitto-dev`    
`cd pathplanning ; make`

## mujocoboard

virtual board to simulate sphero movement on path commands

### setup

[Install Mujoco](https://blog.guptanitish.com/blog/install-mujoco/). 
If using conda, make a soft link from the local /usr/lib/x86_64-linux-gnu/libstdc++.so.6 to 
the corresponding file in your conda env.

make sure the LD_PRELOAD env variable is setup to render mujoco:     
`export LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libGLEW.so`

### run
make a go virtual board environment xml with a random stone placement:    
`python make_env.py`   

run the mujoco simulation using board.xml:    
`python virtualboard.py`

### Using Repositories

[alpha-zero-general](https://github.com/suragnair/alpha-zero-general)   
[sphero_formation (0ac14aad3)](https://github.com/mkrizmancic/sphero_formation)
[sphero_ros](github.com:mmwise/sphero_ros)