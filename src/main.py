import asyncio
import sys

from log import Log
from repeater import Repeater


async def main():
    repeater = Repeater()
    repeater.start()
    while True:
        await asyncio.sleep(1.0)


if __name__ == '__main__':
    Log.setup()
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        sys.exit()
