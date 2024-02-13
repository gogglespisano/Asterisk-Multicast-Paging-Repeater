from asyncio import Lock


class AsyncList(list):
    def __init__(self):
        super().__init__()
        self.__lock = Lock()

    async def __aenter__(self):
        await self.__lock.acquire()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.__lock.release()
