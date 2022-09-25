rolling stones play go

## installation

1. ROS2: [ROS2 installation instructions](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debians.html)

2. Package dependencies:    
refer to [ros2 workspace setup instructions](https://docs.ros.org/en/foxy/Tutorials/Beginner-Client-Libraries/Creating-A-Workspace/Creating-A-Workspace.html).   
ROS uses system python3 interpreter. Use `python -m pip install <package>` to manually install tensorflow, keras, and ros-related packages.
If you are using conda, make sure to deactivate the current environment before installing.

bluez:   
`python3 -m pip install setuptools==57.5.0`    
`python3 -m pip install bluez`

3. clone sphero_ros: https://github.com/mmwise/sphero_ros   
`git clone git@github.com:mmwise/sphero_ros.git` 

## Docker

bluez and other dependencies are included in the image

### Setup

`docker pull ymyrvolod/rspg`

### Run with a local sphero
1. kill bluetoothd so it can be started in the container:   
`sudo killall -9 bluetoothd`
2. `docker run -it --privileged --net=host --name rspg rspg`
3. `source /rosws/install/setup.bash`    
4. `roscore > /dev/null &`    
5. `cd /rosws/src/sphero_ros/sphero_nodes/nodes/ && python3 sphero.py`
   

## Known Issues

Bluetooth scanning isn't working in python, while it works in bluetoothctl.

## Using Repositories

[alpha-zero-general](https://github.com/suragnair/alpha-zero-general)   
[sphero_formation (0ac14aad3)](https://github.com/mkrizmancic/sphero_formation)