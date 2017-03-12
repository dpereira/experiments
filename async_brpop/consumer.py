import asyncio
import aioredis

async def reply(client, task):
    if task in (b'task_0',):
        print('Waiting to reply to %s' % task)
        await asyncio.sleep(10)

    print('Replying %s' % task)
    await client.rpush(task.decode(), task)
    print('Replied %s' % task)

async def consume(client):
    key, task = await client.blpop('tasks')
    print('Received %s' % task)
    return task

async def run(loop):
    client = await aioredis.create_redis(
        ('localhost', 6379),
        loop=loop
    )

    tasks = []

    count = 0
    while True:
        count += 1
        task = await consume(client)
        tasks.append(asyncio.ensure_future(reply(client, task)))
        if count % 7 == 0:
            print('Waiting tasks: %s' % tasks)
            await asyncio.wait(tasks)
            tasks = []


loop = asyncio.get_event_loop()
loop.run_until_complete(run(loop))
