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
import uuid
import pymongo
#import telebot
import random
import time
import pandas
from langdetect import detect


class AudioStreamer():
  def __init__(self,call):
    self.logger = ColouredLogger("audio sharing")
    self.channels = 1
    self.sample_rate = 8000
    self.vad = webrtcvad.Vad()
    self.vad.set_mode(3)
    self.noise_frames_threshold = int(2 * self.sample_rate / 512)
    self.noise_frames_count = 0
    self.call=call
    self.w = 0
    self.v = 320
    self.level = 1
    try:
       pandas.read_csv("test.csv")
    except Exception as e:
        self.testdf=pandas.DataFrame()
    self.audioplayback=False   
    self.silent_frames_count=0   
    self.combined_audio = b''  
    self.channel="en"
    self.long_silence=0
    self.noise=False
    self.call_flow_num=0
    self.last_level=0
    self.call_id=str(uuid.uuid4())
    self.long_silence=0
    self.intent="welcome"
    self.lang_change=False
    with open("db.txt") as f:
       data=f.read()
    print(data)
    if data.endswith("\n"):
       data=data.strip("\n")

    try:
      self.conn = pymongo.MongoClient(data)
    except Exception as e:
      self.logger.info(e)
  
    

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

  def send_audio(self,audio_file):

    self.logger.info("Sending audio file of length {}".format(len(audio_file)/(320*25)))
    count = 0
    w=0
    v=320
    sleep_seconds=0
    self.audioplayback=True
    for i in range(math.floor(int(len(audio_file) / (320)))):
      self.call.write(audio_file[w:v])
      w += 320
      v += 320
     
      #self.detect_noise(indata, 1, 8000)
      count+=1
      if count%25==0:
        sleep(.25)
        sleep_seconds+=.25
      # if self.level!=11:
      if not self.noise:
        if self.noise_frames_count >= 20:
            self.noise=True
            
          
            self.noise_frames_count=0
            self.audioplayback=False
            return
    
    self.logger.info("number of iterations are {}".format(count))
    sleep(len(audio_file)/16000-sleep_seconds)  
    self.logger.info(sleep_seconds)
    self.logger.info("Sleeping for {} seconds".format((len(audio_file)/16000)-sleep_seconds))
    self.noise_frames_count=0
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
      self.long_silence+=1
      
    else:
      self.long_silence=0
  
    return
  

  def detect_long_silence(self,indata,frames,rate):
      samples = np.frombuffer(indata, dtype=np.int16)
      is_noise = self.vad.is_speech(samples.tobytes(), rate)
      frames=0
      if not is_noise:
        #self.logger.debug("Noise detected in frames {0}".format(self.noise_frames_count))
        frames+=1
        
        if frames>200:

          self.long_silence=+1
          return
        else:
          return


  def start_noise_detection(self):
    while self.call.connected:
      audio_data = self.call.read()
      self.combined_audio+=audio_data
      self.dedect_silence(audio_data,1,8000)
       # self.logger.info("silence detection started the value of silent fames is {}".format(self.silent_frames_count))  
    return
  
  def start_polling(self):
    self.bot.polling()
  def convert_file(self,file):
    # Decode and combine u-law fragments into a single bytearray
    # Remove the unused line of code
    # combined_pcm_data = bytearray()

    # ulaw_data = bytes(file['data']['data'])

    # Decode the u-law data to 16-bit linear PCM
    # pcm_data = audioop.ulaw2lin(file, 2)

    # Save the combined PCM data to a WAV file
    filename='output{}.wav'.format(random.randint(1000, 9999))
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)  # Adjust based on the number of channels in your audio
        wf.setsampwidth(2)  # 2 bytes for 16-bit audio
        wf.setframerate(8000)  # Adjust based on the sample rate of your u-law audio
        wf.writeframes(file)
        return filename
    
  def is_english(self,text):
          try:
              lang = detect(text)
              return lang == 'en'
          except:
              return False
  def db_entry(self,resp,mapping):
         database_entry={"audio":self.combined_audio,
                                "text":resp['transcribe'],
                                "nlp":resp['nlp'],
                                "level":self.level,
                                "intent":self.intent,
                                "lang":self.channel,
                                "interuption":self.noise,
                                "call_id":self.call_id,
                                "file_played":mapping[self.channel][self.call_flow_num][self.intent][self.level]
                                }
         try:
          x=self.conn["test"]["test"].insert_one(database_entry)
          self.logger.info("data inserted into db")
          self.logger.info(x)
         except Exception as e:
          self.logger.error(e)
        
         return

  

  def start_audio_playback(self,mapping):
    self.logger.info('Received connection from {0}'.format(self.call.peer_addr))
    while self.call.connected:
        #start timing the duration of the call
        timestart=time.time()
       
        if not self.audioplayback:
            while self.long_silence<10:
                sleep(.2)
                self.logger.info("sleeping for 0.2 seconds")
            self.logger.info("we are in level {}.wav".format(self.level))
            x = self.read_wave_file("demo_audios/resp/{}.wav".format(self.level))
            self.send_audio(x)
            sleep(10)
            self.call.hangup()
        #     self.level+=1
        #     self.long_silence=0
        # if self.level==3:
        #    self.call.hangup()
        

        

        
            

           

       
        

        #convert data to json
        #response=requests.post("http://localhost:5005/convert",data=self.combined_audio)
        #self.logger.info(response.text)
        


    print('Connection with {0} over'.format(self.call.peer_addr))
    timeend=time.time()
    self.testdf=self.testdf.append({"call_id":self.call_id,"duration":timeend-timestart},ignore_index=True)
    self.testdf.to_csv("test.csv")
    return


def handel_call():

  audiosocket=Audiosocket(("localhost",1123))
  while True:
    call=audiosocket.listen()
    stream=AudioStreamer(call)
    noise_stream=threading.Thread(target=stream.start_noise_detection)
    noise_stream.start()
    playback_stream=threading.Thread(target=stream.start_audio_playback,args=(mapping,))
    playback_stream.start()
    
    
  
handel_call()

