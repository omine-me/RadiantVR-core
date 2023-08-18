# how to decide which lights to turn on
# from mathutils import Vector
import math
import numpy as np
from config import config

from dmxout import out

x=0; y=0; z=0
# config = {
#     "max_watt": 1400,
#     "lights": {
#         0: {
#             "loc": (x, y, 0),
#             "watt": 120,
#         },
#         1: {
#             "loc": (x, y, 1),
#             "watt": 120,
#         },
#         2: {
#             "loc": (x, y, 2),
#             "watt": 120,
#         },
#         3: {
#             "loc": (x, y, 3),
#             "watt": 120,
#         },
#     }
# }

def distance(vec1, vec2):
    return math.sqrt((vec1[0]-vec2[0])**2 + (vec1[1]-vec2[1])**2 + (vec1[2]-vec2[2])**2)


def compute_intensity(heat_sources):
    # player is at (0,0,0)
    # each heat source has its location(m), intensity(照度?), radius(m)
    # heat_sources = {
    #             0: {
    #                 "loc": (0,0,5),
    #                 "intensity": 10,
    #                 "radius": .3
    #             },
    #             1: {
    #                 "loc": (0,0,5),
    #                 "intensity": 10,
    #                 "radius": .3
    #             },
    #         }

    # each output is corresponds to each light. So len(outputs) == len(num of lights) 
    outputs = []

    for idx, light in config["lights"].items():
        out_intensity = 0
        
        for heat in heat_sources.values():
            if np.dot(heat["loc"], light["loc"]) < 0:
                # heatとlightが反対方向にある時は考慮しない
                continue
            # out_intensity += (1/(Vector(heat["loc"]) - Vector(light["loc"])))
            # radius, intensityは逆２乗に従わせる
            out_intensity += (1/max((distance(heat["loc"], light["loc"])-heat["radius"]), 0.0001)) * heat["intensity"]# * (heat["radius"])

        out_intensity *= 90
        if out_intensity < 0: out_intensity = 0
        elif 255 < out_intensity: out_intensity = 255
        out_intensity = int(out_intensity)
        outputs.append(out_intensity)

    assert len(config["lights"]) == len(outputs)
    # print(outputs)
    return outputs