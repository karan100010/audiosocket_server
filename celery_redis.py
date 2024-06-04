from celery_redis import Celery

app = Celery('proj',
            broker='redis://172.16.1.209:6379/0', backend='redis://172.16.1.209:6379/0',
             include=['proj.tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
)

if __name__ == '__main__':
    app.start()