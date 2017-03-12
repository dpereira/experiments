import asyncio
import aioredis

async def produce(client, count):
    num_tasks = await client.rpush('tasks', 'task_%s' % count)
    print('Sent %s, %s total tasks in queue' % (count, num_tasks))

async def get_result(client, count):
    task = 'task_%s' % count
    print('Waiting for %s' % task)
    key, task = await client.blpop(task)
    print('Received result for %s' % task)

async def run(loop):
    clients = []
    for i in range(4):
        clients.append(await aioredis.create_redis(
            ('localhost', 6379),
            loop=loop
        ) )
        
    tasks = []
    objects = []
    for i in range(7):
        await produce(clients[i % 4], i)

    for i in range(7):
        f = get_result(clients[i % 4], i)
        objects.append(f)
        tasks.append(asyncio.ensure_future(f))

    print('All sent.')
    await asyncio.wait(tasks)
    print('All done.')

loop = asyncio.get_event_loop()
loop.run_until_complete(run(loop))
