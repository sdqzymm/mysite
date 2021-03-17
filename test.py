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

# asyncio.run( func() )


# 读者编者问题->编者优先
from threading import Thread, Semaphore
from queue import PriorityQueue

q = PriorityQueue(10)
read_count = 0
edit_count = 0
s_read_count = Semaphore(1)
s_edit_count = Semaphore(1)
s_type = Semaphore(1)
s_priority = Semaphore(1)


def reader(name):
    global edit_count
    global read_count

    s_priority.acquire()
    s_priority.release()

    s_read_count.acquire()
    read_count += 1
    if read_count == 1:
        s_type.acquire()
    s_read_count.release()

    print(f'{name}开始读书')
    time.sleep(5)
    print(f'{name}读完书')

    s_read_count.acquire()
    read_count -= 1
    if read_count == 0:
        s_type.release()

    s_read_count.release()


def editor(name):
    global edit_count
    s_edit_count.acquire()
    edit_count += 1
    if edit_count == 1:
        s_priority.acquire()
    s_edit_count.release()

    s_type.acquire()
    print(f'{name}开始编辑')
    time.sleep(10)
    print(f'{name}编辑完毕')
    s_type.release()

    s_edit_count.acquire()
    edit_count -= 1
    if edit_count == 0:
        s_priority.release()
    s_edit_count.release()


class MyThread(Thread):
    def __init__(self, target, name, type, *args, **kwargs):
        super(MyThread, self).__init__(target=target, name=name, args=args, kwargs=kwargs)
        self.type = type


threads = []
for i in range(5):
    threads.append(MyThread(reader, f'{2*i}', 'reader', f'reader{i}'))
    threads.append(MyThread(editor, f'{2*i+1}', 'editor', f'editor{i}'))

random.shuffle(threads)
[t.start() for t in threads]



