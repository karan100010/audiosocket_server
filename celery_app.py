from celery import Celery

# Configure the Celery application
app = Celery('audiosocket_server',
             broker='redis://localhost:6379/0',
         
             include=['audiosocket_server.tasks'])


# Optional configuration
app.conf.update(
    result_backend='redis://localhost:6379/0',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_send_task_events = True,  # Enable task events
task_send_sent_event = True  # Enable sending task-sent events
)

if __name__ == '__main__':
    app.start()


