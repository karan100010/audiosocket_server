#!/usr/bin/env python3
# Standard Python modules
from time import sleep
# Import everything from the audiosocket module
from audiosocket import *
from asterisk.agi import *
from pydub import AudioSegment
from pydub.utils import make_chunks

agi = AGI()


# Create a new Audiosocket instance, passing it binding
# information in a tuple just as you would a raw socket
audiosocket = Audiosocket(("localhost", 1121))

# This will block until a connection is received, returning
# a connection object when one occurs
conn = audiosocket.listen()


print('Received connection from {0}'.format(conn.peer_addr))
agi.answer()
agi.verbose("python agi started")

# While a connection exists, send all
# received audio back to Asterisk (creates an echo)
audio_file="../output.wav"
  #convert the wav file to ulaw
  

myaudio = AudioSegment.from_file(audio_file , "wav") 
chunk_length_ms = 1000 # pydub calculates in millisec
chunks = make_chunks(myaudio, chunk_length_ms) #Make chunks of one sec

#Convert chunks to raw audio data which you can then feed to HTTP stream
for i, chunk in enumerate(chunks):
    conn.write(chunk.raw_data)
while conn.connected:
  audio_data = conn.read()
  #read a wav file from the system and convert it to ulaw
  



 


print('Connection with {0} over'.format(conn.peer_addr))
