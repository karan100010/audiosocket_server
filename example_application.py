#!/usr/bin/env python3
# Standard Python modules
from time import sleep
# Import everything from the audiosocket module
from audiosocket import *
from pydub import AudioSegment
from pydub.utils import make_chunks
import numpy as np
import sounddevice as sd
import webrtcvad 
import wave

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
while True:
  
  for i in  range(int(len(myaudio)/320)):
      conn.write(myaudio[w:v])
      w+=320
      v+=320
  if noise_frames_count>=20:
    print("Noise detected ending stream")
    break


#Convert chunks to raw audio data which you can then feed to HTTP stream


while conn.connected:
  audio_data = conn.read()
  # Detect noise
  detect_noise(audio_data, 1, 8000)
  print(noise_frames_count)
  if noise_frames_count >= noise_frames_threshold:
    print("Noise detected, hanging up")
    conn.hangup()
    break
   
  #read a wav file from the system and convert it to ulaw
  



 


print('Connection with {0} over'.format(conn.peer_addr))
