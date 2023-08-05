import asyncio
from pyartnet import ArtNetNode
from config import config
from random import randint

def adjust_watt(config, intensities):
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

async def out(intensities):
    # Run this code in your async function
    node = ArtNetNode('127.0.0.1', 6454)

    # Create universe 0
    universe = node.add_universe(0)

    # Add a channel to the universe which consists of 3 values
    # Default size of a value is 8Bit (0..255) so this would fill
    # the DMX values 1..3 of the universe
    channel = universe.add_channel(start=1, width=len(config["lights"]))

    # adjust intensities not to exceed max_watt
    intensities = adjust_watt(config, intensities)

    channel.set_fade(intensities, 100)
    # channel.set_values([randint(0,255),randint(0,255),randint(0,255)])

    # this can be used to wait till the fade is complete
    await channel

# for _ in range(50):
#     asyncio.run(out())
