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
from langdetect import detect
import socket
#from asterisk.manager import Manager



class AudioStreamer():
  def __init__(self,socket,call):
    self.logger = ColouredLogger("audio sharing")
    self.channels = 1
    self.sample_rate = 8000
    self.vad = webrtcvad.Vad()
    self.vad.set_mode(3)
    self.noise_frames_threshold = int(2 * self.sample_rate / 512)
    self.noise_frames_count = 0
    self.call=call
    self.audiosocket=socket
    #self.uudi=self.audiosocket.uudi
    self.uuid=call.uuid
    self.w = 0
    self.v = 320
    self.level = 0
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
    # #self.manager=Manager()
    
    # self.manager.connect("localhost")
    # self.manager.login('karan', 'test')

    
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
  
    self.callflow=self.conn["test"]["callflow"].find_one({"call_id":"uuid"})

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
      # write stream to a file
      # with open("stream.txt", "ab") as f:
      #   f.write(audio_data)
      if self.audioplayback:
        #self.logger.info("noise detection started the value of noise fames is {}".format(self.noise_frames_count))
        self.detect_noise(audio_data, 1, 8000)
      else:
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
        self.logger.info("the uuid for this call is {}".format(self.uuid))
       
        if not self.audioplayback:
            self.logger.info("we are in level {}".format(self.level))
            x = self.read_wave_file(mapping[self.channel][self.call_flow_num][self.intent][self.level])
            self.send_audio(x)
            #self.call.hangup()
          
            #disconnet call from audio socket
            



            if self.intent!="welcome":
               
              if self.noise:
                x=self.read_wave_file(mapping["utils"][self.channel][0])
                self.send_audio(x)
                self.noise=False
            while self.long_silence<100:
              sleep(.01)
            self.long_silence=0
              
           
          
  
            
        
            try:
              response=requests.post("http://172.16.1.209:5002/convert_{}".format(self.channel),data=self.combined_audio)
              m= self.convert_file(self.combined_audio)
              self.logger.info("audio file converted {}".format(m))
              resp=json.loads(response.text)
              print(resp)
              return
              threading.Thread(target=self.db_entry,args=(resp,mapping)).start()
              
              self.combined_audio=b''
              
            
              if resp["transcribe"]=="":
                x=self.read_wave_file(mapping["utils"][self.channel][1])
                self.send_audio(x)
              
              

          
            except Exception as e:
              self.logger.info(e)
              self.combined_audio=b''
              #self.call.hangup()
            # if resp["transcribe"]=="":
            #     self.level="cant_hear"
            if self.level==0 and self.intent=="welcome" and self.call_flow_num==0 and self.channel=="en":
                if  detect(resp["transcribe"]) != "en":
                   
                   self.lang_change=True
            if resp["nlp"]["intent"]=="positive":
                if self.intent!="welcome":
                  self.level+=1
                
                self.intent="positive"
  
            elif resp["nlp"]["intent"]=='negative':
                if  self.intent!="welcome":
                  self.level+=1
                self.intent="negative"
            if mapping[self.channel][self.call_flow_num][self.intent][self.level]=="change_flow":
              if self.call_flow_num==0:

                self.call_flow_num+=1
                self.level=0
                self.intent="welcome"
              else:
                self.call_flow_num-=1
                self.level=0
                self.intent="welcome"
        
            if mapping[self.channel][self.call_flow_num][self.intent][self.level]=="end_call":
              self.call.hangup()
              self.audioplayback=False
              sleep(1)

            if self.lang_change:
              self.channel="hi"
              self.level=0
              self.intent="welcome"
              self.call_flow_num=0
              self.logger.info("changing channel to hindi")
              self.lang_change=False
          

            
            


        
            # if self.level==1:
            #   self.level=2

            # elif self.level==2:
            #   while self.silent_frames_count<100:
            #         print("waiting")
            #         sleep(.01)
            #response=requests.post("http://65.2.152.189:5000/predict",data=self.combined_audio)
            #   resp=json.loads(response.text)
            #   print(resp)
            #   self.level=resp["prediction"][0]

              
            # elif self.level=="hi" or self.level== "en":
            #   self.call.hangup()
          

            # if self.level==11:
            #   sleep(1)
            #   x=self.read_wave_file(mapping[self.channel][self.level])
            #   self.send_audio(x)
            #   self.logger.info("playing interuption message")

            #self.logger.info("audio length is "+str(self.read_length(mapping[self.channel][self.level])) + " seconds")
            # if self.level==8:
            #   self.call.hangup()
            #   self.audioplayback=False
            #   sleep(1)
            # if self.level!=9:
            #   while self.silent_frames_count<100:
            #     sleep(.01)
            #   self.logger.info("waiting for silence")
            #   self.silent_frames_count=0
            #   self.data_array=[]
              
            #   try:
            #     response=requests.post("http://3.109.152.180:5002/convert_en",data=self.combined_audio)
            #     resp=json.loads(response.text)
            #   except Exception as e:
            #     self.logger.info(e)
            #     resp={"transcribe":"error","nlp":"error"}
            #   if resp['transcribe']!="error":
            #     print(resp)
            
            #     try:
                  
            #       self.conn["test"]["test"].insert_one(database_entry)
            #     except Exception as e:
            #       self.logger.info(e)
                
              


                              
            
            #   self.combined_audio=b''
              
            #   if self.level!=11:
            #     self.last_level=self.level
            #     self.level=9
            #   else:
            #     self.level=self.last_level
            # else:
            #   self.level=self.last_level+1

          # if self.level==11:
          #   self.level=self.noise_level
          #   x=self.read_wave_file(mapping[self.channel][self.level])
          #   self.send_audio(x)
          # else:
          #   self.level+=1
        
            




          #   while noise - self.noise_level < 10:
          #     x=self.read_wave_file(mapping[self.channel][self.level])
          #     self.send_audio(x)
          #     self.logger.info("audio length is "+str(self.read_length(mapping[self.channel][self.level])) + " seconds")
          #     self.silent_frames_count=0
          #     self.level=10
          #   else:
          #     self.level=last_level
         

            #  if self.level==11:
            #   x=self.read_wave_file(mapping[self.channel][self.level])
            #   self.logger.info("Call inturrupted due to noise")
            #   self.send_audio(x)
              
              
            #   while self.silent_frames_count<75:
            #     sleep(.01)
            #   self.level=last_level
            #  else:
            #   x=self.read_wave_file(mapping[self.channel][self.level])
            #   self.logger.info("Call inturrupted due to noise")
            #   self.send_audio(x)
              
              
            #   while self.silent_frames_count<75:
            #     sleep(.01)
            #   self.level=last_level



        self.logger.info("silent frames count is {}".format(self.silent_frames_count))
        

        #convert data to json
        #response=requests.post("http://localhost:5005/convert",data=self.combined_audio)
        #self.logger.info(response.text)
        


    print('Connection with {0} over'.format(self.call.peer_addr))


def handel_call():

  audiosocket=Audiosocket(("localhost",1122))
  while True:
    call=audiosocket.listen()

    stream=AudioStreamer(audiosocket,call)
    noise_stream=threading.Thread(target=stream.start_noise_detection)
    noise_stream.start()
    playback_stream=threading.Thread(target=stream.start_audio_playback,args=(mapping,))
    playback_stream.start()
    

    
  
handel_call()

