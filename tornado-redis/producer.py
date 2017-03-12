from tornado.platform.asyncio import AsyncIOMainLoop
import tornado.platform.asyncio
import tornado
import asyncio
import tornado.gen
import aioredis
import uuid
import json
import time

def produce(count, client, prefix='task_'):
    task_id = prefix + str(uuid.uuid1())
    r = client.rpush('tasks', json.dumps([task_id, count]))
    return task_id

@tornado.gen.coroutine
def sync(client, i, task_id):
    key, data = yield client.blpop(task_id)
    print('Got %s' % key)
    r = json.loads(data.decode())
    task_id2, count = r
    assert task_id == task_id2
    assert count == i
    print('%s: %s' % (i, r))

@tornado.gen.coroutine
def run(loop):
    client = yield aioredis.create_redis(
        ('localhost', 6379),
        loop=loop
    )
    tasks = []
    fs = []

    for i in range(50000):
        task_id = produce(i, client)
        fs.append(sync(client, i, task_id))
        if i % 1000:
            yield tornado.gen.sleep(0.01)

    print('All tasks sent')
    yield from fs

    client.close()
    yield client.wait_closed()

AsyncIOMainLoop().install()
loop = asyncio.get_event_loop()
loop.run_until_complete(tornado.platform.asyncio.to_asyncio_future(run(loop)))
