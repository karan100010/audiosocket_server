# your_module/tasks.py

from celery_app import app

@app.task
def add(x, y):
    return x + y

@app.task
def multiply(x, y):
    return x * y

@app.task
def sum_list(numbers):
    return sum(numbers)
if __name__ == '__main__':
    result=add.delay(4,4)
    print(result)