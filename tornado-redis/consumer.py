from tornado.platform.asyncio import AsyncIOMainLoop
from concurrent.futures import ThreadPoolExecutor
import tornado.platform.asyncio
import tornado
import tornado.ioloop
import asyncio
import tornado.gen
import tornado.concurrent
import aioredis
import uuid
import json
import random
import time

@tornado.gen.coroutine
def process(client, task_id, count):
    r = client.rpush(task_id, json.dumps([task_id, count]))
    print('%s done' % task_id)

@tornado.gen.coroutine
def consume(client, prefix='task_'):
    key, data = yield client.brpop('tasks', timeout=1200)
    task_id, count = json.loads(data.decode())
    print('Got %s with id %s' % (count, task_id))
    process(client, task_id, count)

@tornado.gen.coroutine
def run(loop):
    client = yield aioredis.create_redis(
        ('localhost', 6379),
        loop=loop
    )   
    while True:
        try:
            yield consume(client)
        except KeyboardInterrupt:
            client.close()
            yield client.await_closed()

AsyncIOMainLoop().install()
loop = asyncio.get_event_loop()
loop.run_until_complete(tornado.platform.asyncio.to_asyncio_future(run(loop)))
