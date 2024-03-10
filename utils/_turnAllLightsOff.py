from pyartnet import ArtNetNode
from config import config
import asyncio


async def out():
    node = ArtNetNode('127.0.0.1', 6454,start_refresh_task=False)

    # Create universe 0
    universe = node.add_universe(0)

    channel = universe.add_channel(start=1, width=len(config["lights"]))

    channel.set_fade([0]*len(config["lights"]), 0)
    await channel

asyncio.run(out())
