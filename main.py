import argparse
import math
import asyncio

from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
from dmxout import out
from compute_intensity import compute_intensity

def print_volume_handler(unused_addr, args, volume):
    print("[{0}] ~ {1}".format(args[0], volume))

def print_compute_handler(unused_addr, args, volume):
    try:
        print("[{0}] ~ {1}".format(args[0], args[1](volume)))
    except ValueError: pass

_interval = 0
player_loc = [0, 0, 0]
player_locY = 0
heat_sources = {}

def rotation_2d(x, y, theta):
    return x*math.cos(theta)-y*math.sin(theta), x*math.sin(theta)+math.cos(theta)


def update_values(key, v1, v2=None, v3=None):
    # print(key, v1,v2,v3)
    global _interval, player_loc, heat_sources

    ### debug ###
    if _interval < 10:
        _interval += 1
        return 
    else:
        _interval = 0
    ###       ###


    if key.startswith("/player"):
        _, _, transform_elm = key.split("/")
        if transform_elm == "loc":
            assert v3 is not None
            player_loc = [v1, v2, v3]
        elif transform_elm == "rotY":
            player_locY = v1
    elif key.startswith("/heatsource"):
        _, _, idx, attr = key.split("/")
        idx = int(idx)
        if v3 is not None: # when loc
            v1, v3 = rotation_2d(v1-player_loc[0], v3-player_loc[2], player_locY)
        try:
            heat_sources[idx] = {**heat_sources[idx], attr: ((v1, v2-player_loc[1], v3) if v3 is not None else v1)}
        except KeyError:
            heat_sources[idx] = {attr: ((v1, v2-player_loc[1], v3) if v3 is not None else v1)}
        # TODO
        # delete heat source when their num decreases
    else:
        ValueError(f"{key} is not defined.")

    intensities = compute_intensity(heat_sources)
    asyncio.run(out(intensities))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip",
        default="127.0.0.1", help="The ip to listen on")
    parser.add_argument("--port",
        type=int, default=8080, help="The port to listen on")
    args = parser.parse_args()

    dispatcher = Dispatcher()
    # dispatcher.map("/*", print)
    #   dispatcher.map("/volume", print_volume_handler, "Volume")
    #   dispatcher.map("/logvolume", print_compute_handler, "Log volume", math.log)
    dispatcher.map("/*", update_values)

    server = osc_server.ThreadingOSCUDPServer(
        (args.ip, args.port), dispatcher)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()
