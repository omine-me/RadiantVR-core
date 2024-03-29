import argparse
import math
import asyncio
from time import time

from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
from utils.dmxout import out
from utils.compute_intensity import compute_intensity

_interval = 0
player_loc = [0, 0, 0]
player_rotY = 0
heat_sources = {}
light_on = False
scene_name = ""
isSteamBigin = False
isInSteam = False
SteamMaxCount = 500
currentSteamCount =0
isInMagma = False

def rotation_2d(x, y, theta):
    return x*math.cos(theta)-y*math.sin(theta), x*math.sin(theta)+y*math.cos(theta)

def invert_axis_x(val):
    return -val
def invert_rot_y(val):
    return -val

def update_values(key, v1, v2=None, v3=None):
    global _interval, player_loc, player_rotY, heat_sources, light_on, scene_name, isSteamBigin, isInSteam, SteamMaxCount, currentSteamCount, isInMagma

    ### debug ###
    # if _interval < 10:
    #     _interval += 1
    #     return 
    # else:
    #     _interval = 0
    ###       ###
    # print(key)
    

    if key.startswith("/isLightsOn"):
        if not v1:
            # print("Light Off")
            light_on = False
            for heat_source in heat_sources.values():
                heat_source["intensity"] = .0
            intensities = [0]*24#compute_intensity(heat_sources, scene_name, player_loc[2], isInSteam, isInMagma)
            asyncio.run(out(intensities))
            return
        else:
            light_on = True
            # print("Light ON")

    if key.startswith("/player"):
        _, _, transform_elm = key.split("/")
        if transform_elm == "loc":
            assert v3 is not None
            player_loc = [v1, v2+.5, v3]
        elif transform_elm == "rotY":
            player_rotY = v1
    elif key.startswith("/heatsource"):
        _, _, idx, attr = key.split("/")
        idx = int(idx)
        # print(idx, attr, v1)
        
        if v3 is not None: # when loc
            v1, v3 = rotation_2d(invert_axis_x(v1-player_loc[0]), v3-player_loc[2], invert_rot_y(player_rotY))
            # v1 = invert_axis_x(v1-player_loc[0])
            # v3 = v3-player_loc[2]
        try:
            heat_sources[idx] = {**heat_sources[idx], attr: ((v1, v2-player_loc[1], v3) if v3 is not None else v1), "time": time()}
        except KeyError:
            heat_sources[idx] = {attr: ((v1, v2-player_loc[1], v3) if v3 is not None else v1), "time": time()}
        # print(heat_sources)
    elif key.startswith("/sceneName"):
        scene_name = v1
    elif key.startswith("/isSteamBigin"):
        if not isInSteam:
            isInSteam = True
    elif key.startswith("/isInMagma"):
        isInMagma = bool(v1)
    else:
        ValueError(f"{key} is not defined.")

    if isInSteam:
        currentSteamCount += 1
        if currentSteamCount > SteamMaxCount:
            isInSteam = False
            currentSteamCount =0


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
        
        intensities = compute_intensity(heat_sources, scene_name, player_loc[2], isInSteam, isInMagma)
        # print(intensities)
        asyncio.run(out(intensities))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip",
        # default="127.0.0.1", help="The ip to listen on")
        default="", help="The ip to listen on")

    parser.add_argument("--port",
        type=int, default=8080, help="The port to listen on")
    args = parser.parse_args()

    import netifaces as ni
    try:
        ip = ni.ifaddresses('en1')[ni.AF_INET][0]['addr']
    except:
        ip = None
    if ip is None:
        for iface in ni.interfaces():
            if ni.AF_INET in ni.ifaddresses(iface):
                ip = ni.ifaddresses(iface)[ni.AF_INET][0]['addr']
                if ip != "127.0.0.1":
                    break
                else:
                    ip =None
    
    if ip is None:
        if not args.ip:
            raise ValueError("Specify IP Addtrss by adding your IP like this 'python main_radiantVR.py --ip 192.169.1.13'")
        ip = args.ip

    
    dispatcher = Dispatcher()
    dispatcher.map("/*", update_values)

    server = osc_server.ThreadingOSCUDPServer(
        (ip, args.port), dispatcher)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()
