import asyncio
from pyartnet import ArtNetNode
from config import config
from random import randint

def check_watt(config, intensities):
    watt_sum = 0
    for light, intensity in zip(config["light"], intensities):
        watt_sum += light["watt"] * intensity
    
    if watt_sum <= config["max_watt"]:
        return True
    else:
        return False

async def main():
    # Run this code in your async function
    node = ArtNetNode('127.0.0.1', 6454)

    # Create universe 0
    universe = node.add_universe(0)

    # Add a channel to the universe which consists of 3 values
    # Default size of a value is 8Bit (0..255) so this would fill
    # the DMX values 1..3 of the universe
    channel = universe.add_channel(start=1, width=3)

    # Fade channel to 255,0,0 in 5s
    # The fade will automatically run in the background
    channel.set_fade([randint(0,255),randint(0,255),randint(0,255)], 100)
    # channel.set_values([randint(0,255),randint(0,255),randint(0,255)])

    # this can be used to wait till the fade is complete
    await channel
for _ in range(50):
    asyncio.run(main())
