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

    self.logger.info("Sending audio file of length {}".format(len(audio_file)/320))
    self.playback=True
    count = 0
    for i in range(math.floor(int(len(audio_file) / 320))):
      self.conn.write(audio_file[self.w:self.v])
      self.w += 320
      self.v += 320
      #self.detect_noise(audio_data, 1, 8000)
      count += 1
      if count%25:
        sleep(1)

     
      if self.noise_frames_count > 4:
        self.level = 4
        self.logger.info("Level has changed to {}".format(self.level))
        return
    self.playback=False
    self.level += 1
    self.logger.info("Level has changed to {}".format(self.level))
    return 
    
  #write a function that reads the lenth of a audiofile in seconds

  def read_length(self, audio_file):
    with wave.open(audio_file, 'rb') as wave_file:
      audio = wave_file.getnframes()
    return audio/8000
    

  def start_noise_detection(self):
    while self.conn.connected:
      audio_data = self.conn.read()
      self.detect_noise(audio_data, 1, 8000)

  def stat_audio_playback(self,mapping):
    while self.conn.connected:
      if self.level == 1:
        if not self.audioplayback:
          x = self.read_wave_file(mapping[1])
          self.send_audio(x)
          self.logger.info("audio lenth is "+str(self.read_length(mapping[1])) + " seconds")
          

      if self.level == 2:
        if not self.audioplayback:
          x = self.read_wave_file(mapping[2])
          self.logger.info("changed to level two")
      
          self.send_audio(x)
          
      if self.level == 3:
        if not self.audioplayback:
          x = self.read_wave_file(mapping[3])
          self.send_audio(x)
          
      if self.level == 4:
        if not self.audioplayback:
          x = self.read_wave_file(mapping[4])
          self.logger.info("Changed to level 4")
          process = threading.Thread(target=self.send_audio, args=(x,))
          process.start()
          


    print('Connection with {0} over'.format(self.conn.peer_addr))

streamer=AudioStreamer()
noise_stream=threading.Thread(target=streamer.start_noise_detection)
noise_stream.start()
audio_stream=threading.Thread(target=streamer.stat_audio_playback,args=(mapping,))
audio_stream.start()
audio_stream.join()

