# Standard Python modules
from threading import Thread

# Audiosocket module
from audiosocket import *


class AudiosocketServer:
  def __init__(self):
    # Create a globally accessible audiosocket instance
    self.audiosocket = Audiosocket(('0.0.0.0', 1122))
    self.audiosocket.prepare_output(outrate=44000, channels=2)
    self.audiosocket.prepare_input(inrate=44000, channels=2)
    print('Listening for new connections from Asterisk on port {0}'.format(self.audiosocket.port))

  def handle_connection(self, call):
    cntr = 0
    print('Received connection from {0}'.format(call.peer_addr))

    while call.connected:
      audio_data = call.read()
      call.write(audio_data)

      # Hangup the call after receiving 1000 audio frames
      if cntr == 1000:
        call.hangup()

      cntr += 1

    print('Connection with {0} is now over'.format(call.peer_addr))

  def start(self):
    while True:
      call = self.audiosocket.listen()

      call_thread = Thread(target=self.handle_connection, args=(call,))
      call_thread.start()


# Create an instance of the AudiosocketServer class and start the server
server = AudiosocketServer()
server.start()
