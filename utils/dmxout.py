from pyartnet import ArtNetNode
from config import config
from pyartnet.output_correction import quadratic
# import asyncio

async def out(intensities):
    # Run this code in your async function
    node = ArtNetNode('127.0.0.1', 6454,start_refresh_task=False)
    # node = ArtNetNode('192.168.1.13', 6454 ,start_refresh_task=False)

    # Create universe 0
    universe = node.add_universe(0)

    # Add a channel to the universe which consists of 3 values
    # Default size of a value is 8Bit (0..255) so this would fill
    # the DMX values 1..3 of the universe
    channel = universe.add_channel(start=1, width=len(config["lights"]))

    # 二乗することでワット数を減少する
    # channel._correction_current = quadratic
    
    channel.set_fade(intensities, 0)
    # channel.set_values(intensities)

    # print(intensities)

    # this can be used to wait till the fade is complete
    await channel

# for _ in range(3):
#     asyncio.run(out([0]*len(config["lights"])))
