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

  def send_audio(self, audio_file, audio_data):
    self.logger.info("Sending audio file of length {}".format(len(audio_file)/320))
    self.playback=True
    for i in range(int(len(audio_file) / 320)):
      self.conn.write(audio_file[self.w:self.v])
      self.w += 320
      self.v += 320
      #self.detect_noise(audio_data, 1, 8000)
      
      sleep(.01)
      if self.noise_frames_count > 4:
        self.level = 4
        self.logger.info("Level has changed to {}".format(self.level))
        return
    self.playback=False
    self.level += 1
    self.logger.info("Level has changed to {}".format(self.level))
    return 
    


  def start_streaming(self, mapping):
    while self.conn.connected:
      audio_data = self.conn.read()

      if self.level == 1:
        if not self.audioplayback:
          x = self.read_wave_file(mapping[1])
          process = threading.Thread(target=self.send_audio, args=(x, audio_data,))
          process.start()
          process.join()
      if self.level == 2:
        if not self.audioplayback:
          x = self.read_wave_file(mapping[2])
          self.logger.info("changed to level two")
          process = threading.Thread(target=self.send_audio, args=(x, audio_data,))
          process.start()
     
        
        process.start()
      if self.level == 3:
        if not self.audioplayback:
          x = self.read_wave_file(mapping[3])
          self.logger.info("changed to level 3")
          process = threading.Thread(target=self.send_audio, args=(x, audio_data,))
          process.start()
          self.conn.hangup()
          
      
      elif self.level == 4:
        if not self.audioplayback:
          x = self.read_wave_file(mapping[4])
          self.logger.info("Changed to level 4")
          process = threading.Thread(target=self.send_audio, args=(x, audio_data,))
          process.start()


    print('Connection with {0} over'.format(self.conn.peer_addr))

streamer=AudioStreamer()
streamer.start_streaming(mapping)
