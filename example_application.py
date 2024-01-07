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
    self.conn = None
    self.w = 0
    self.v = 320
    self.level = 1

  def read_wave_file(self, filename):
    self.logger.debug("Reading wave file")
    with wave.open(filename, 'rb') as wave_file:
      audio = wave_file.readframes(wave_file.getnframes())
    return audio

  def detect_noise(self, indata, frames, rate):
    self.logger.debug("Detecting noise")
    samples = np.frombuffer(indata, dtype=np.int16)
    is_noise = self.vad.is_speech(samples.tobytes(), rate)
    if is_noise:
      self.logger.debug("Noise detected")
      self.noise_frames_count += frames

  def send_audio(self, audio_file, url, port, service=""):
    for i in range(int(len(audio_file) / 320)):
      self.conn.write(audio_file[self.w:self.v])
      self.w += 320
      self.v += 320
      self.logger.debug("Sending audio")
      sleep(.005)
      self.detect_noise(audio_data, 1, 8000)
      if self.noise_frames_count > 4:
        self.logger.debug("Noise detected")
        file = self.read_wave_file(mapping[4])
        j = 0
        k=320
        for i in range(int(len(file) / 320)):
          self.conn.write(file[self.w:self.v])
          self.j += 320
          self.k += 320
          self.logger.debug("Sending audio")
          sleep(.005)
        self.level = 4
        sys.exit()
      else:
        self.level += 1

  def start_streaming(self,mapping):
    self.audiosocket = Audiosocket(("localhost", 1122))
    self.conn = self.audiosocket.listen()
    print('Received connection from {0}'.format(self.conn.peer_addr))
    audio_file = "../output.wav"
    myaudio = self.read_wave_file(audio_file)
    process = threading.Thread(target=self.send_audio, args=(myaudio,))
    process.start()
    while self.conn.connected:
      audio_data = self.conn.read()
      if self.level == 1:
        process = threading.Thread(target=self.send_audio, args=(mapping[1],))
        process.start()
      if self.level == 2:
        process = threading.Thread(target=self.send_audio, args=(mapping[2],))
        process.start()
        val = 0
      if self.level == 3:
        process = threading.Thread(target=self.send_audio, args=(mapping[3],))
        process.start()
        val = 0
    print('Connection with {0} over'.format(self.conn.peer_addr))

streamer=AudioStreamer()
streamer.start_streaming(mapping)