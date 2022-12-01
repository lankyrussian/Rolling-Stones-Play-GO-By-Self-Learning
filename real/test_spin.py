from spherov2 import scanner
from spherov2.sphero_edu import SpheroEduAPI
import time

# ADDRESS = (
#     "C8:94:81:DA:1C:88"
# )
characteristic = "00010002-574f-4f20-5370-6865726f2121"

def move(api, x, y):
    if(x>=0):
        api.spin(90, 1)
        api.set_speed(20)
        time.sleep(abs(x))
        api.set_speed(0)
        api.spin(270, 1)
    elif(x<0):
        api.spin(270, 1)
        api.set_speed(20)
        time.sleep(abs(x))
        api.set_speed(0)
        api.spin(90, 1)
    if (y >= 0):
        api.set_speed(20)
        time.sleep(abs(y))
        api.set_speed(0)
    elif(y<0):
        api.spin(180, 1)
        api.set_speed(20)
        time.sleep(abs(y))
        api.set_speed(0)
        api.spin(180,1)

for i in range(10):
    try:
        # toy = scanner.find_toys(toy_names=["SB-1C88","SB-174A"])
        toy = scanner.find_toy(toy_name="SB-1C88")
        with SpheroEduAPI(toy) as api:
            # api.set_speed(30)
            time.sleep(2)
            # api.set_speed(0)
            print(f"Sphero named {toy} has orientation {api.get_orientation()}")

            move(api, -2, 0)
            print(f"Sphero named {toy} has orientation {api.get_orientation()}")
            # api.spin(90,1)
            print(f"Sphero named {toy} has orientation {api.get_orientation()}")
            # api.spin(90,1)
            print(f"Sphero named {toy} has orientation {api.get_orientation()}")
            # print(f"Sphero named {toy} has orientation {api.get_location()}")
            # api.set_speed(30)
            # time.sleep(2)
            # api.set_speed(0)
            # print(f"Sphero named {toy} has orientation {api.get_location()}")
        break
    except Exception as e:
        print(e)

