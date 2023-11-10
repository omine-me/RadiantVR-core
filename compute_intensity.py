import math
import numpy as np
from config import config

# this function prevents unexpected watt over occures when many middle ranged values exist. 
def _many_middle_range_intensities(intensities):
    assert len(intensities)
    within_middle_count = sum([1 if 70<intensity<150 else 0 for intensity in intensities])
    # print(intensities)
    if within_middle_count > 9:
        return True
    return False

def _many_high_range_intensities(intensities):
    high_count = sum([1 if 240<intensity else 0 for intensity in intensities])
    if high_count > 17:
        return True
    return False

# adjust intensities not to exceed max_watt
def adjust_watt(intensities):
    # gamma = 2
    # correction_
    # print(intensities)

    are_many_middle = _many_middle_range_intensities(intensities)
    are_many_high = _many_high_range_intensities(intensities)

    watt_sum = 0
    for light, intensity in zip(config["lights"].values(), intensities):
        linear_value = light["watt"] * intensity / 255.
        # if are_many_middle:
        #     linear_value *= light["loc"][1]
        #     print("middle range adjusted", light["loc"][1])
        # if are_many_high:
        #     linear_value *= light["loc"][1]/1.4
        watt_sum += linear_value
        # watt_sum += 255.*((linear_value/255.)**(1/gamma))
        # watt_sum += light["watt"] * math.sin(linear_value / 255. * math.pi/2)
    
    if watt_sum <= config["max_watt"]:
        return intensities
    else:
        factor = config["max_watt"]/watt_sum# * .9
        # factor = config["max_watt"]/watt_sum * .8 # .77は上に凸な非線型なグラフから上手いとこ合わせられそうななんとなくの値

        assert factor < 1
        intensities = [int(intensity * factor) for intensity in intensities]
        if are_many_high:
            print("high")
            intensities = [int(intensity * max(0,(config["lights"][idx]["loc"][1] - 1.2)*2.5+1.2)) for idx, intensity in enumerate(intensities)]
        if are_many_middle:
            print("middle")
            intensities = [int(intensity * config["lights"][idx]["loc"][1]/1.4) for idx, intensity in enumerate(intensities)]


        ### DEBUG ###
        watt_sum = 0
        for light, intensity in zip(config["lights"].values(), intensities):
            linear_value = light["watt"] * intensity / 255.
            watt_sum += linear_value
            # watt_sum += 255.*((linear_value/255.)**(1/gamma))
            # watt_sum += light["watt"] * math.sin(linear_value / 255. * math.pi/2)
        print("Adjust to", int(watt_sum), "w")
        if not watt_sum <= config["max_watt"]+50:
            intensities = [0] * len(intensities)
            print("OVER CAPACITY EVEN AFTER ADJUSTING!!!")
        #############

        return intensities


def distance(vec1, vec2):
    return math.sqrt((vec1[0]-vec2[0])**2 + (vec1[1]-vec2[1])**2 + (vec1[2]-vec2[2])**2)


def compute_intensity(heat_sources, scene_name, player_loc_y, isInSteam):
    # player is at (0,0,0)
    # each heat source has its location(m), intensity(照度?), radius(m)

    # each output is corresponds to each light. So len(outputs) == len(num of lights) 
    outputs = []
    # print(heat_sources)

    if scene_name == "sauna":
        if player_loc_y > -5.5:
            if isInSteam:
                return [152,56,38,0,148,0,0,113,0,150,0,100,0,170,0,0,170,70,55,0,188,75,0]
            else:
                return [102, 0,0,0,100,0,0,107,0,107,0,107,0,110,0,0,110,0,0,0,105,0,0]
        else:
            return [0]*len(config["lights"])
            

    if scene_name == "cave":
        power = 3.7
    elif scene_name == "Introduction":
        power = 4
    else:
        power = 3

    for idx, light in config["lights"].items():
        out_intensity = 0
        
        for heat in heat_sources.values():
            if np.dot(heat["loc"], light["loc"]) < 0:
                # heatとlightが反対方向にある時は考慮しない
                continue
            # out_intensity += (1/max((distance(heat["loc"], light["loc"])-heat["radius"]), 0.0001)) * heat["intensity"]# * (heat["radius"])
            dot = np.dot(heat["loc"], light["loc"]) # 0 〜 1
            radius = heat["radius"] / distance(heat["loc"], (0,0,0))
            out_intensity += ((heat["intensity"]*dot*radius) / (distance(heat["loc"], (0,0,0))**power)) * (light["loc"][1]/1.25 if scene_name=="park" else 1)
            # print(out_intensity)

        out_intensity *= 40#30000

        if out_intensity < 0: out_intensity = 0
        elif 255 < out_intensity: out_intensity = 255
        out_intensity = int(out_intensity)
        outputs.append(out_intensity)
    
    # assert len(config["lights"]) == len(outputs)

    outputs = adjust_watt(outputs)

    return outputs