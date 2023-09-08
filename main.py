import argparse
import math
import asyncio
from time import time

from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
from dmxout import out
from compute_intensity import compute_intensity

_interval = 0
player_loc = [0, 0, 0]
player_rotY = 0
heat_sources = {}
light_on = False

def rotation_2d(x, y, theta):
    return x*math.cos(theta)-y*math.sin(theta), x*math.sin(theta)+y*math.cos(theta)

def invert_axis_x(val):
    return -val
def invert_rot_y(val):
    return -val

def update_values(key, v1, v2=None, v3=None):
    global _interval, player_loc, player_rotY, heat_sources, light_on

    ### debug ###
    # if _interval < 10:
    #     _interval += 1
    #     return 
    # else:
    #     _interval = 0
    ###       ###
    # print(key, v1,v2,v3)

    if key.startswith("/isLightsOn"):
        if not v1:
            # print("Light Off")
            light_on = False
            for heat_source in heat_sources.values():
                heat_source["intensity"] = .0
            intensities = compute_intensity(heat_sources)
            asyncio.run(out(intensities))
            return
        else:
            light_on = True
            # print("Light ON")

    if key.startswith("/player"):
        _, _, transform_elm = key.split("/")
        if transform_elm == "loc":
            assert v3 is not None
            player_loc = [v1, v2, v3]
        elif transform_elm == "rotY":
            player_rotY = v1
    elif key.startswith("/heatsource"):
        _, _, idx, attr = key.split("/")
        idx = int(idx)
        
        if v3 is not None: # when loc
            v1, v3 = rotation_2d(invert_axis_x(v1-player_loc[0]), v3-player_loc[2], invert_rot_y(player_rotY))
            # v1 = invert_axis_x(v1-player_loc[0])
            # v3 = v3-player_loc[2]
        try:
            # if attr == "loc" and idx == 0:
            #     print(v2, player_loc[1])
            heat_sources[idx] = {**heat_sources[idx], attr: ((v1, v2-player_loc[1], v3) if v3 is not None else v1), "time": time()}
        except KeyError:
            heat_sources[idx] = {attr: ((v1, v2-player_loc[1], v3) if v3 is not None else v1), "time": time()}
    else:
        ValueError(f"{key} is not defined.")


    if _interval < 3:
        _interval += 1
        return 
    else:
        if not light_on:
            return
        _interval = 0
        # delete unused sources considering by last updated time
        curr_time = time()
        heat_sources = {k: v for k, v in heat_sources.items() if (curr_time - v["time"] < .3)}

        intensities = compute_intensity(heat_sources)
        # print(intensities)
        asyncio.run(out(intensities))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip",
        default="127.0.0.1", help="The ip to listen on")
    parser.add_argument("--port",
        type=int, default=8080, help="The port to listen on")
    args = parser.parse_args()

    dispatcher = Dispatcher()
    dispatcher.map("/*", update_values)

    server = osc_server.ThreadingOSCUDPServer(
        (args.ip, args.port), dispatcher)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()
