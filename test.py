import asyncio
import time
import random

class Reader():
    def __init__(self):
        self.count = 0

    async def read(self):
        self.count += 1
        if self.count == 100:
            return None
        return self.count

    def __aiter__(self):
        return self

    async def __anext__(self):
        val = await self.read()
        if val == None:
            raise StopAsyncIteration
        return val

async def func():
    reader = Reader()
    async for item in reader:
        print(item)

asyncio.run( func() )