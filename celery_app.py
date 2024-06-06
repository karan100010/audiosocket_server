from celery import Celery

# Configure the Celery application
app = Celery('tasks', broker='redis://localhost:6379/0')

# Optional configuration
app.conf.update(
    result_backend='redis://localhost:6379/0',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)



