import asyncio

from repeater import Repeater


async def main():
    repeater = Repeater()
    repeater.start()
    while True:
        await asyncio.sleep(1.0)


if __name__ == '__main__':
    asyncio.run(main())
