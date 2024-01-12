#!/usr/bin/env python3
# Standard Python modules
from time import sleep
from audiosocket import *
import numpy as np
import webrtcvad
from mylogging import ColouredLogger
import wave
import threading
import sys
import requests
from mapping import *
import math
from req import Requsts

class AudioStreamer:
  def __init__(self):
    self.logger = ColouredLogger("audio sharing")
    self.channels = 1
    self.sample_rate = 8000
    self.vad = webrtcvad.Vad()
    self.vad.set_mode(3)
    self.noise_frames_threshold = int(2 * self.sample_rate / 512)
    self.noise_frames_count = 0
    self.audiosocket = Audiosocket(("localhost", 1122))
    self.conn =  self.audiosocket.listen()
    self.w = 0
    self.v = 320
    self.level = 1
    self.audioplayback=False                            


  def read_wave_file(self, filename):
    #self.logger.debug("Reading wave file")
    with wave.open(filename, 'rb') as wave_file:
      audio = wave_file.readframes(wave_file.getnframes())
    return audio

  def detect_noise(self, indata, frames, rate):
    
    samples = np.frombuffer(indata, dtype=np.int16)
    is_noise = self.vad.is_speech(samples.tobytes(), rate)
    if is_noise:
      #self.logger.debug("Noise detected in frames {0}".format(self.noise_frames_count))
      self.noise_frames_count += frames

  def send_audio(self, audio_file):

    self.logger.info("Sending audio file of length {}".format(len(audio_file)/(320*25)))
    count = 0
    w=0
    v=320
    sleep_seconds=0
    self.audioplayback=True
    for i in range(math.floor(int(len(audio_file) / (320)))):
      self.conn.write(audio_file[w:v])
      w += 320
      v += 320
     
      #self.detect_noise(audio_data, 1, 8000)
      count+=1
      if count%25==0:
        sleep(.25)
        sleep_seconds+=.25

      if self.noise_frames_count >= 4:
        self.level = 4
        self.logger.info("Level has changed to {}".format(self.level))
        
        return
    self.logger.info("number of iterations are {}".format(count))
    sleep(len(audio_file)/16000-sleep_seconds)  
    
    self.logger.info(sleep_seconds)
    self.logger.info("Sleeping for {} seconds".format((len(audio_file)/16000)-sleep_seconds))
    return
    
    
  #write a function that reads the lenth of a audiofile in seconds

  def read_length(self, audio_file):
    with wave.open(audio_file, 'rb') as wave_file:
      audio = wave_file.getnframes()
    return audio/8000
  
    

  def start_noise_detection(self):
    while self.conn.connected:
      audio_data = self.conn.read()
      self.logger.info("noise detection started the value of noise fames is {}".format(self.noise_frames_count))
      self.detect_noise(audio_data, 1, 8000)

  def start_audio_playback(self,mapping):
    while self.conn.connected:

        if not self.audioplayback:
        
          x = self.read_wave_file(mapping[self.level])
          self.send_audio(x)
          self.logger.info("audio length is "+str(self.read_length(mapping[1])) + " seconds")
          if self.level != 4:
            self.level+=1
          else:
            pass  
          self.audioplayback=False


  
          


    print('Connection with {0} over'.format(self.conn.peer_addr))

streamer=AudioStreamer()
noise_stream=threading.Thread(target=streamer.start_noise_detection)
noise_stream.start()
streamer.start_audio_playback(mapping)


