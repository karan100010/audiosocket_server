#!/usr/bin/env python3
# Standard Python modules
from time import sleep
# Import everything from the audiosocket module
from audiosocket import *
from asterisk.agi import *
from pydub import AudioSegment
from pydub.utils import make_chunks

import wave

def read_wave_file(filename):
    with wave.open(filename, 'rb') as wave_file:
        audio = wave_file.readframes(wave_file.getnframes())
    return audio


# Create a new Audiosocket instance, passing it binding
# information in a tuple just as you would a raw socket
audiosocket = Audiosocket(("localhost", 1122))

# This will block until a connection is received, returning
# a connection object when one occurs
conn = audiosocket.listen()


print('Received connection from {0}'.format(conn.peer_addr))

# While a connection exists, send all
# received audio back to Asterisk (creates an echo)
audio_file="../output.wav"
  #convert the wav file to ulaw
  

myaudio=read_wave_file(audio_file)
#splitting the audio file into chunks of 16-bit, 8kHz, mono PCM
w=0
v=320
for i in  range(int(len(myaudio)/320)):
    conn.write(myaudio[w:v])
    w+=320
    v+=320


#Convert chunks to raw audio data which you can then feed to HTTP stream


while conn.connected:
  audio_data = conn.read()
  #read a wav file from the system and convert it to ulaw
  



 


print('Connection with {0} over'.format(conn.peer_addr))
