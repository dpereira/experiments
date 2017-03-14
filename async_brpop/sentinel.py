import asyncio
import aioredis

loop = asyncio.get_event_loop()

async def go():
    conn = await aioredis.create_connection(
        ('localhost', 26379), 
        loop=loop
    )
    result = await conn.execute('sentinel', 'get-master-addr-by-name','mymaster')
    print(result)
    conn.close()
    await conn.wait_closed()

loop.run_until_complete(go())
