from simple_celery.task import task

import tornado
import tornado.ioloop
import tornado.gen
from concurrent.futures import ThreadPoolExecutor


class Executor:
    io_loop = tornado.ioloop.IOLoop.current()
    executor = ThreadPoolExecutor(4)

    @tornado.concurrent.run_on_executor
    def run(self, count):
        try:
            r = task.apply_async(args=[count])
            return r.wait()
        except Exception as e:
            print('%s %s' % (type(e), e))
            return 0

def tcelery_run(count):
    return tornado.gen.Task(task.apply_async, args=[count])

@tornado.gen.coroutine
def run():
    e = Executor()
    tasks = []
    for i in range(100):
        r = e.run(i)
        #r = tcelery_run(i)
        tasks.append(r)

    #yield tornado.gen.sleep(10)

    for t in tasks:
        r = yield t
        print('%s' % r)

    print('DONE')


io_loop = tornado.ioloop.IOLoop.current()
io_loop.run_sync(run)
