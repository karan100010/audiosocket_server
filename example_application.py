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
import json
import base64

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
    self.w = 0
    self.v = 320
    self.level = 1
    self.audioplayback=False   
    self.silent_frames_count=0   
    self.combined_audio = b''  
    self.channel="en"


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

  def send_audio(self, call,audio_file):

    self.logger.info("Sending audio file of length {}".format(len(audio_file)/(320*25)))
    count = 0
    w=0
    v=320
    sleep_seconds=0
    self.audioplayback=True
    for i in range(math.floor(int(len(audio_file) / (320)))):
      call.write(audio_file[w:v])
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
        self.noise_frames_count = 0
        
        return
    self.logger.info("number of iterations are {}".format(count))
    sleep(len(audio_file)/16000-sleep_seconds)  
    self.logger.info(sleep_seconds)
    self.logger.info("Sleeping for {} seconds".format((len(audio_file)/16000)-sleep_seconds))
    self.audioplayback=False
    return
    
    
  #write a function that reads the lenth of a audiofile in seconds

  def read_length(self, audio_file):
    with wave.open(audio_file, 'rb') as wave_file:
      audio = wave_file.getnframes()
    return audio/8000
  
  def dedect_silence(self,indata,frames,rate):
    samples = np.frombuffer(indata, dtype=np.int16)
    is_noise = self.vad.is_speech(samples.tobytes(), rate)
    if not is_noise:
      #self.logger.debug("Noise detected in frames {0}".format(self.noise_frames_count))
      self.silent_frames_count += frames



  def start_noise_detection(self,call):
    while call.connected:
      audio_data = call.read()
      if self.audioplayback:
       # self.logger.info("noise detection started the value of noise fames is {}".format(self.noise_frames_count))
        self.detect_noise(audio_data, 1, 8000)
      else:
        self.combined_audio+=audio_data
        self.dedect_silence(audio_data,1,8000)
       # self.logger.info("silence detection started the value of silent fames is {}".format(self.silent_frames_count))  
    return
  def start_audio_playback(self,call,mapping):
    self.logger.info('Received connection from {0}'.format(call.peer_addr))
    while call.connected:

        if not self.audioplayback:
          
          x = self.read_wave_file(mapping["en"][1])
          self.send_audio(call,x)
          #self.logger.info("audio length is "+str(self.read_length(mapping[self.channel][self.level])) + " seconds")

          self.audioplayback=False
          sleep(1)

        while self.silent_frames_count<100:
          sleep(.01)
          #self.logger.info("silent frames count is {}".format(self.silent_frames_count))
        

        #convert data to json
        response=requests.post("http://localhost:5005/convert",data=self.combined_audio)
        #self.logger.info(response.text)
        self.data_array=[]
        self.silent_frames_count=0
        self.level+=1


    print('Connection with {0} over'.format(call.peer_addr))

  def handel_call(self):
    
    while True:
      call = self.audiosocket.listen()
      noise_stream=threading.Thread(target=self.start_noise_detection,args=(call,))
      noise_stream.start()
      playback_stream=threading.Thread(target=self.start_audio_playback,args=(call,mapping,))
      playback_stream.start()
    
audiosocket=AudioStreamer()
audiosocket.handel_call()

