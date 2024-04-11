from time import sleep
from audiosocket import *


socket = Audiosocket(('localhost', 1122))
call=socket.listen()
print(call.read())