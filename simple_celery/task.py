import celery

app = celery.Celery()

#app.conf.broker_url = 'amqp://localhost:5672'
#app.conf.result_backend = 'amqp://localhost:5672'


app.conf.broker_url = 'redis://localhost:6379/0'
#app.conf.result_backend = 'redis://localhost:6379/1'
#app.conf.result_backend = 'rpc://'
#app.conf.redis_max_connections = 10000

#app.conf.result_backend = 'db+mysql://root:my-secret-pw@127.0.0.1:3306/celery_results'


@app.task
def task(count):
    print('RUNNING %s' % count)
    return count


