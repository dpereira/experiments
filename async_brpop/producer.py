import asyncio
import aioredis

async def produce(client, count):
    num_tasks = await client.rpush('tasks', 'task_%s' % count)
    print('Sent %s, %s total tasks in queue' % (count, num_tasks))

async def get_result(count, loop, readers=[]):
    print('%s total readers active' % len(readers))
    try:
        reader = readers.pop()
    except IndexError:
        reader = await aioredis.create_redis(
            ('localhost', 6379),
            loop=loop
        )
    task = 'task_%s' % count
    print('Waiting for %s' % task)
    key, task = await reader.blpop(task, timeout=20)
    print('Received result for %s' % task)
    readers.append(reader)

async def run(loop):
    client = await aioredis.create_redis(
        ('localhost', 6379),
        loop=loop
    )
    readers = []
       
   
    wtasks = []
    rtasks = []

    num_messages = 10000

    for i in range(num_messages):
        f =  produce(client, i)
        wtasks.append(asyncio.ensure_future(f))

        f = get_result(i, loop, readers)
        rtasks.append(asyncio.ensure_future(f))

        if len(rtasks) >= 10:
            print('%s max rtasks reached, syncing' % (len(rtasks)))
            print('Free readers PRIOR: %s' % len(readers))
            rtasks = list(filter(lambda f: not f.done(), rtasks))
            if rtasks:
                await asyncio.wait(rtasks, return_when=asyncio.FIRST_COMPLETED)
            print('Free readers AFTER: %s' % len(readers))

    print('All sent.')
    await asyncio.wait(wtasks + rtasks)
    print('All done.')
    print('Had to spawn %s readers' % len(readers))

    for r in readers + [client]:
        r.close()
        await r.wait_closed()

loop = asyncio.get_event_loop()
loop.run_until_complete(run(loop))
