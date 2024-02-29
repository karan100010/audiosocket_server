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
import telebot
import random


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
    self.audioplayback=False   
    self.silent_frames_count=0   
    self.combined_audio = b''  
    self.channel="en"
    self.long_silence=0
    self.noise_level=0
    self.last_level=0
    self.call_id=str(uuid.uuid4())
    self.bot_api_token="7144846540:AAGMzRZRmlV8NtQQfQ67vD5butARXFL4tCM"
    self.bot = telebot.TeleBot(self.bot_api_token)
    self.bot.add_message_handler(self.send_audio_tg)
    self.filepath=""
    self.chat_id=""
    self.long_pause=0
    self.conn= pymongo.MongoClient("mongodb+srv://root:toor@testcluster.exl8ah5.mongodb.net/Grievance?retryWrites=true&w=majority&appName=TestCluster",uuidRepresentation='standard')
  def read_chatid(self):
    with open("chat_id.txt", 'r') as file:
          lines = file.readlines()
          # Remove newline characters from each line and return the list
          return [line.strip() for line in lines]

  def send_audio_tg(self, message):
        if self.level==3:
          if self.filepath!="":
            audio = open(self.filepath, 'rb') 
            self.bot.send_audio(message.chat.id, audio)
            audio.close()
        else:
          self.send_message(message.chat.id,"there is some issue on the user end")

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
      if self.level!=11:
        if self.noise_frames_count >= 4:
          self.noise_level = self.level
          self.level = 11
          self.logger.info("Level has changed to {}".format(self.level))
        
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
      self.long_pause+=1
    else:
      self.long_pause=0
    
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
      if self.audioplayback:
        #self.logger.info("noise detection started the value of noise fames is {}".format(self.noise_frames_count))
        self.detect_noise(audio_data, 1, 8000)
      else:
        self.combined_audio+=audio_data
        self.dedect_silence(audio_data,1,8000)
        self.logger.info("silence detection started the value of silent fames is {}".format(self.silent_frames_count))  
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
  

  def start_audio_playback(self,mapping):
    self.logger.info('Received connection from {0}'.format(self.call.peer_addr))
    while self.call.connected:

        if not self.audioplayback:
            self.logger.info("we are in level {}".format(self.level))
            x = self.read_wave_file(mapping[self.channel][self.level])
            self.send_audio(x)
        
            if self.level==1:
              self.level=2

            elif self.level==2:
              while self.long_pause<200:
                    print("waiting")
                    sleep(.01)
              self.filepath=self.convert_file(self.combined_audio)
              self.level=3
              ids=self.read_chatid()
              for id in ids:
                TOKEN="7144846540:AAGMzRZRmlV8NtQQfQ67vD5butARXFL4tCM"
                audio_file=open(self.filepath,"rb")
                url = "https://api.telegram.org/bot"+TOKEN+"/sendAudio"
                files = {'audio': audio_file.read()}
                params = {'chat_id': id}
                def send_audio():
                  response = requests.post(url, files=files, params=params)
                  print(response)
                  return
                send=threading.Thread(target=send_audio)
                send.start()
                def get_analysis():
                  response=requests.post("http://localhost:5000/predict",data=self.combined_audio)
                
                  url = "https://api.telegram.org/bot"+TOKEN+"/sendMessage"
                  
                  #get "transcript" form response
                  dataset = dict(response.json())
                 
                  for i,j in dataset.items():
                    if j!="":
                      

                      data = {"chat_id": id, "text":i+" = "+str(j)}
                      response2 = requests.post(url, data=data)
                      print(response2.text)
                  dataset["audio"]=self.combined_audio
                  try:
                    self.conn["Grievance"]["grievances"].insert_one(dataset)

                  except Exception as e:
                    self.logger.error(e)

                  return
                analysis=threading.Thread(target=get_analysis)
                analysis.start()
              
              
              
            elif self.level==3:
              self.call.hangup()
          

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
            #     database_entry={"audio":self.combined_audio,
            #                     "text":resp['transcribe'],
            #                     "nlp":resp['nlp'],
            #                     "level":self.level,
            #                     "call_addr":self.call.peer_addr,
            #                     "call_id":self.call_id}
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
        

        # #convert data to json
        # def send_stream(self):
        #   self.logger.info("sending stream")
        #   response=requests.post("http://localhost:5000/predict",data=self.combined_audio)
        #   self.logger.info(response.text)
        
        #self.logger.info(response.text)
        


    print('Connection with {0} over'.format(self.call.peer_addr))


def handel_call():

  audiosocket=Audiosocket(("localhost",1122))
  while True:
    call=audiosocket.listen()
    stream=AudioStreamer(call)
    noise_stream=threading.Thread(target=stream.start_noise_detection)
    noise_stream.start()
    playback_stream=threading.Thread(target=stream.start_audio_playback,args=(mapping,))
    playback_stream.start()
    

    
  
handel_call()

