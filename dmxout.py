import asyncio
from pyartnet import ArtNetNode

async def main():
    # Run this code in your async function
    node = ArtNetNode('127.0.0.1', 6454)

    # Create universe 0
    universe = node.add_universe(1)

    # Add a channel to the universe which consists of 3 values
    # Default size of a value is 8Bit (0..255) so this would fill
    # the DMX values 1..3 of the universe
    channel = universe.add_channel(start=1, width=3)

    # Fade channel to 255,0,0 in 5s
    # The fade will automatically run in the background
    channel.add_fade([255,0,0], 1000)

    # this can be used to wait till the fade is complete
    await channel

asyncio.run(main())