import math
import numpy as np
from config import config

# adjust intensities not to exceed max_watt
def adjust_watt(intensities):
    watt_sum = 0
    for light, intensity in zip(config["light"], intensities):
        watt_sum += light["watt"] * intensity
    
    if watt_sum <= config["max_watt"]:
        return intensities
    else:
        intensities = intensities*(config["max_watt"]/watt_sum)

        ### DEBUG ###
        watt_sum = 0
        for light, intensity in zip(config["light"], intensities):
            watt_sum += light["watt"] * intensity
        assert watt_sum <= config["max_watt"]
        #############

        return intensities


def distance(vec1, vec2):
    return math.sqrt((vec1[0]-vec2[0])**2 + (vec1[1]-vec2[1])**2 + (vec1[2]-vec2[2])**2)


def compute_intensity(heat_sources):
    # player is at (0,0,0)
    # each heat source has its location(m), intensity(照度?), radius(m)

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

    outputs = adjust_watt(outputs)

    return outputs