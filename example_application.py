#!/usr/bin/env python3
# Standard Python modules
from time import sleep
# Import everything from the audiosocket module
from audiosocket import *
from pydub import AudioSegment
from pydub.utils import make_chunks
import numpy as np
import webrtcvad 
import wave
import threading
import sys
# Parameters for audio streaming
channels = 1
sample_rate = 8000  # You may need to adjust this based on your audio source

# Parameters for VAD
vad = webrtcvad.Vad()
vad.set_mode(3)  # Aggressiveness mode (0 to 3)

# Variables for noise detection
noise_frames_threshold = int(2 * sample_rate / 512)  # 2 seconds
noise_frames_count = 0

#read a wav file 
def read_wave_file(filename):
    with wave.open(filename, 'rb') as wave_file:
        audio = wave_file.readframes(wave_file.getnframes())
    return audio

# Function to detect noise
def detect_noise(indata, frames,rate):
    global noise_frames_count

    # Convert the audio data to 16-bit integers
    samples = np.frombuffer(indata, dtype=np.int16)
    
    # Perform noise detection using VAD
    is_noise = vad.is_speech(samples.tobytes(), rate)

    if is_noise:
        noise_frames_count += frames




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

def send_audio(audio_file):
  global w
  global v
  global noise_frames_count
  for i in range(int(len(audio_file)/320)):
      
      conn.write(audio_file[w:v])
      w+=320
      v+=320
      print("Sending audio")
      #if i is devisable by 5 enter sleep for .1 seconds
      if i%5==0:
        sleep(.1)
      
      if noise_frames_count>10:
        sys.exit()
# try:
#   send_audio(myaudio)
  
  
# except Exception as e:
#   print(e)    
#call send_audio asychronously
process=threading.Thread(target=send_audio,args=(myaudio,))



  
    #read a wav file from the system and convert it to ulaw

process.start()
while conn.connected:
  audio_data = conn.read()
  # Detect noise
  detect_noise(audio_data, 1, 8000)
  print(noise_frames_count)

  
  #read a wav file from the system and convert it to ulaw
  



 


print('Connection with {0} over'.format(conn.peer_addr))
