Playing Go with Sphero robots

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
   
### Run a go game against a random agent
1. `docker run -it --privileged --net=host --name rspg rspg`
2. `source /rosws/install/setup.bash`
3. `roscore > /dev/null &`
4. `cd /rosws/src/Rolling-Stones-Play-GO-By-Self-Learning/src/ && python3 play.py`

## Known Issues

Bluetooth scanning isn't working in python, while it works in bluetoothctl.

## Using Repositories

[alpha-zero-general](https://github.com/suragnair/alpha-zero-general)   
[sphero_formation (0ac14aad3)](https://github.com/mkrizmancic/sphero_formation)
[sphero_ros](github.com:mmwise/sphero_ros)