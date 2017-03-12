from tornado.platform.asyncio import AsyncIOMainLoop
from concurrent.futures import ThreadPoolExecutor
import tornado.platform.asyncio
import tornado
import tornado.concurrent
import asyncio
import tornado.gen
import aioredis
import uuid
import json
import time

class Sync:
    executor = ThreadPoolExecutor()

    def __init__(self):
        self.io_loop = asyncio.get_event_loop()

    @tornado.concurrent.run_on_executor
    def run(self, task_id, count, client):
        print('waiting  %s' % task_id)
        key, data = yield client.blpop(task_id)
        print('Got %s' % key)
        r = json.loads(data.decode())
        task_id2, count = r
        assert task_id == task_id2
        assert count == i
        print('%s: %s' % (i, r))

@tornado.gen.coroutine
def do_push(client, task_id, count):
    r = yield client.rpush('tasks', json.dumps([task_id, count]))

def produce(count, client, prefix='task_'):
    task_id = prefix + str(uuid.uuid1())
    do_push(client, task_id, count)
    return task_id

@tornado.gen.coroutine
def run(loop):
    client = yield aioredis.create_redis(
        ('localhost', 6379),
        loop=loop
    )

    tasks = []
    fs = []

    s = Sync()

    for i in range(20):
        task_id = produce(i, client)
        tasks.append(task_id)
        print('Sent %s' % i)
        tasks
        fs.append(s.run(client, i, task_id))
        print('Synced %s' % i)
        if i % 1000:
            yield tornado.gen.sleep(0.01)

    print('All tasks sent')
    for i in fs:
        yield fs


    yield tornado.gen.sleep(60)

    client.close()
    yield client.wait_closed()

AsyncIOMainLoop().install()
loop = asyncio.get_event_loop()
loop.run_until_complete(tornado.platform.asyncio.to_asyncio_future(run(loop)))
