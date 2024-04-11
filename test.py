from time import sleep
from audiosocket import *
from threading import Thread


socket = Audiosocket(('localhost', 1122))
call=socket.listen()
x=Thread(call._process())
x.start()
print(call.read())
print(socket.uuid)