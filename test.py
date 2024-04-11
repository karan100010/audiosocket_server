from time import sleep
from audiosocket import *


socket = Audiosocket(('localhost', 1122))
call=socket.listen()
call._process()
print(call.read())
print(socket.uuid)