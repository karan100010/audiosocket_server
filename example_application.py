#!/usr/bin/env python3
# Standard Python modules
from time import sleep
from audiosocket import *
import numpy as np
from vad import *
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
import webrtcvad
# import telebot
import datetime
import random
from langdetect import detect
import socket
# from asterisk.manager import Manager

class AudioStreamer():
    def __init__(self, socket):
        self.logger = ColouredLogger("audio sharing")
        self.channels = 1
        self.flow_num=0
        self.sample_rate = 8000
        self.vad = webrtcvad.Vad()
        self.vad.set_mode(3)
        self.noise_frames_threshold = int(2 * self.sample_rate / 512)
        self.noise_frames_count = 0
        self.audiosocket = socket
        self.call = socket.listen()
        self.long_noise=0
        self.noise=False
        self.startcall = False
        self.combined_byts=b''
        # self.uudi=self.audiosocket.uudi
        self.uuid = str(self.call.uuid)
        self.num_connected = 0
        self.w = 0
        self.v = 320
        self.level = 0
        self.audioplayback = False
        self.silent_frames_count = 0
        self.combined_audio = b''
        self.channel = "en"
        self.long_silence = 0
        self.noise = False
        self.last_level = 0
        self.call_id = str(uuid.uuid4())
        self.long_silence = 0
        self.intent = "welcome"
        self.call_api = "http://localhost:5011/api/connections"
        self.call_link="http://172.16.1.213:3022/call-records/{}".format(self.uuid)
        respdict = requests.get(self.call_link
            ).text
        self.respdict = json.loads(respdict)
        try:
            self.welcome = self.respdict["data"]["intro_rec"]
        except Exception as e:
            self.welcome = "http://172.16.1.207:8084/karan.wav"
            self.logger.error("welcome audio not found {}".format(e))
        

        try:
            self.master =  self.respdict["data"]["master_rec"]
        except Exception as e:

            self.master = "http://172.16.1.207:8084/130302750R_KOTAKV1063666LAPSE.wav"
            self.logger.error("master audio not found {}".format(e))    
        self.master_audio= requests.get(self.master).content
        self.welcome_audio = requests.get(self.welcome).content
        data={"status":"active","addr":"172.16.1.209"+":"+str(self.audiosocket.port),"conn":0,"time_updates":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        json_data=json.dumps(data)
        self.headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'}
        req=requests.post(self.call_api,data=json_data,headers=self.headers)
        print(req.text)

        self.lang_change = False
        with open("db.txt") as f:
            data = f.read()
        print(data)
        if data.endswith("\n"):
            data = data.strip("\n")

        try:
            self.conn = pymongo.MongoClient(data)
        except Exception as e:
            self.logger.info(e)
        self.call_flow=self.conn["test"]["flow"].find_one({})      

    def read_wave_file(self, filename):
        # self.logger.debug("Reading wave file")
        with wave.open(filename, 'rb') as wave_file:
            audio = wave_file.readframes(wave_file.getnframes())
        return audio

    def update_and_hangup(self):
        self.call.hangup()

        return

    def detect_noise(self, indata, frames, rate):

        try:
            #samples = np.frombuffer(indata, dtype=np.int16)
            is_noise = is_speech(indata, rate)
            if is_noise:
                self.logger.debug("Noise detected in frames {0}".format(self.long_noise))
                self.noise_frames_count += frames
                self.long_noise+=1
            else:
                self.long_noise=0
            if self.noise_frames_count>10:
                self.startcall=True
            return
        except Exception as e:
            self.logger.info("error occered while trying to dedect silence {}".format(e))


    def send_audio(self,audio_file):

        self.logger.info("Sending audio file of length {}".format(len(audio_file)/(320*25)))
        count = 0
        w=0
        v=320

        self.audioplayback=True
        for i in range(math.floor(int(len(audio_file) / (320)))):
            self.call.write(audio_file[w:v])
            w += 320
            v += 320
            
            #self.detect_noise(indata, 1, 8000)
            count+=1
          
            if count%25==0:
                sleep(.5)
                #sleep_seconds+=.25
            if not self.noise:
                if self.long_noise >= 20:
                    self.noise=True
                    self.noise_frames_count=0
                    self.audioplayback=False
                    return
        
        # self.logger.info("number of iterations are {}".format(count))
        # sleep(len(audio_file)/16000-sleep_seconds)  
        # self.logger.info(sleep_seconds)
        # self.logger.info("Sleeping for {} seconds".format((len(audio_file)/16000)-sleep_seconds))
        self.noise_frames_count=0
        self.audioplayback=False
        return
            

    def read_length(self, audio_file):
        with wave.open(audio_file, 'rb') as wave_file:
            audio = wave_file.getnframes()
        return audio/8000

    def dedect_silence(self, indata, frames, rate):
       # samples = np.frombuffer(indata, dtype=np.int16)
        is_noise = is_speech(indata, rate)
        #print(is_noise)
        if not is_noise:
           # self.logger.debug("Noise detected in frames {0}".format(self.noise_frames_count))
            self.silent_frames_count += frames
            self.long_silence += 1
            
        else:
            self.long_silence = 0
        return

    def start_noise_detection(self):
         

        while self.call.connected:
            

            # requests.post(self.call_api,data={"call_id":self.call_id,"status":"active","addr":self.audiosocket.addr+":"+str(self.audiosocket.port)})
            audio_data = self.call.read()
            combined_byts=self.call.read_for_vad()
            

           


            if self.audioplayback:
                #self.logger.info("noise detection started the value of noise fames is {}".format(self.noise_frames_count))
                self.detect_noise(self,combined_byts, 1, 8000)
            else:
                self.combined_audio += audio_data
                self.dedect_silence(combined_byts, 1, 8000)
               # self.logger.info("silence detection started the value of silent fames is {}".format(self.silent_frames_count))
        return

    def convert_file(self, file):
        # Decode and combine u-law fragments into a single bytearray
        # Remove the unused line of code
        # combined_pcm_data = bytearray()
       # pcm_data = audioop.ratecv(file, 2, 1, 8000,6000, None)[0]
      
        #pcm_data = audioop.lin2lin(pcm_data, 2,2)

        # ulaw_data = bytes(file['data']['data'])

        # Decode the u-law data to 16-bit linear PCM
        # pcm_data = audioop.ulaw2lin(file, 2)

        # Save the combined PCM data to a WAV file
        filename = 'output.wav'
        with wave.open(filename, 'wb') as wf:
            # Adjust based on the number of channels in your audio
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 2 bytes for 16-bit audio
            # Adjust based on the sample rate of your u-law audio
            wf.setframerate(7000)
            wf.writeframes(file)
            return filename

    def is_english(self, text):
        try:
            lang = detect(text)
            return lang == 'en'
        except:
            return False

    def db_entry(self, resp, mapping):
        database_entry = {"audio": self.combined_audio,
                          "text": resp['transcribe'],
                          "nlp": resp['nlp'],
                          "level": self.level,
                          "intent": self.intent,
                          "lang": self.channel,
                          "interuption": self.noise,
                          "call_id": self.call_id
                          }
        try:
            x = self.conn["test"]["test"].insert_one(database_entry)
            self.logger.info("data inserted into db")
            self.logger.info(x)
        except Exception as e:
            self.logger.error(e)

        return

    def start_audio_playback(self, mapping):
        self.logger.info(
            'Received connection from {0}'.format(self.call.peer_addr))

    
        if self.call.connected:

            self.logger.info("the uuid for this call is {}".format(self.uuid))
            self.logger.info(self.uuid)
            self.num_connected += 1
            update_data={"addr":"172.16.1.209"+":"+str(self.audiosocket.port),"update":{"conn":self.num_connected}}
            update_data=json.dumps(update_data)
            requests.put(self.call_api+"/update",update_data,headers=self.headers)  
            try:
                self.welcome = self.respdict["data"]["intro_rec"]
            except Exception as e:
                self.welcome = "http://172.16.1.207:8084/hello.wav"
                self.logger.error("welcome audio not found {}".format(e)) 
            self.audioplayback=True        
            while not self.startcall:
            #    self.logger.info("waiting for call to start")
                sleep(.1)
            self.audioplayback=False
            self.logger.info("call started")
            self.noise_frames_count=0
            self.long_noise=0
            while self.call.connected:

            
             if not self.audioplayback:
                self.logger.info("audio playback started")
                self.logger.info("we are in level {}".format(self.level))
                self.logger.error(self.intent)


                if not self.noise:     

                
                    if self.level==0:
                        self.send_audio(self.welcome_audio)
                    #handeling level 1
                    elif self.level==1 and self.intent=="yes_intent" and self.flow_num==0:

                        self.send_audio(self.master_audio)
                        self.logger.info("sending master audio")

                    else:
                        
                        
                        try:
                            audio=requests.get(self.call_flow["main_audios"][self.intent+"_"+str(self.level)][self.flow_num][0])
                            self.logger.warning("level is {}".format(self.level))
                            self.logger.warning("intent is {}".format(self.intent))
                            self.logger.warning("flow num is {}".format(self.flow_num))
                        
                            self.send_audio(audio.content)
                            self.logger.info("sending other audios")
                            if self.intent=="contact_human_agent" or self.intent=="other_intent":
                                self.logger.error("contat human agent activated")
                                data= {"call_id":self.uuid,"hangup":"none","transfer":"true"}
                                x=self.conn["test"]["calls"].insert_one(data)
                                self.call.hangup()
                                
                        except Exception as e:
                            self.logger.error("audio playback failed beacause of {}".format(e))

                    if self.level==0:
                        self.level+=1
                    elif self.call_flow["main_audios"][self.intent+"_"+str(self.level)][self.flow_num][1]["meta"]=="next_level":
                        self.level+=1
                        self.logger.info("new level is {}".format(self.level))
                    elif self.call_flow["main_audios"][self.intent+"_"+str(self.level)][self.flow_num][1]["meta"]=="hangup":
                        if self.call_flow["main_audios"][self.intent+"_"+str(self.level)][self.flow_num][1]["silence"]:
                            self.long_silence=0
                            while self.long_silence<100:
                                if self.call.connected:
                                    sleep(.2)
                                else:
                                    break
                            if not self.call.connected:
                                break

                        
                        try:
                                    self.logger.info("{} found at level 3".format(self.intent))
                                    data= {"call_id":self.uuid,"hangup":"true","transfer":"none"}
                                    x=self.conn["test"]["calls"].insert_one(data)
                                    audio= requests.get(self.call_flow["utils"]["bye"])
                                    self.send_audio(audio.content)
                                    self.call.hangup()
                        except Exception as e:
                            self.logger.error("audio playback failed beacause of {}".format(e))
                    elif self.call_flow["main_audios"][self.intent+"_"+str(self.level)][self.flow_num][1]["meta"]=="transfer":
                        
                        try:
                                    self.logger.info("{} found at level 3".format(self.intent))
                                    data= {"call_id":self.uuid,"hangup":"none","transfer":"true"}
                                    x=self.conn["test"]["calls"].insert_one(data)
                                    audio= requests.get(self.call_flow["utils"]["bye"])
                                    self.send_audio(audio.content)
                                    self.call.hangup()
                        except KeyError as e:
                            self.logger.error("audio playback failed beacause of {}".format(e))
                        except Exception as e:
                            self.logger.error("audio playback failed beacause of {}".format(e))
                    elif self.call_flow["main_audios"][self.intent+"_"+str(self.level)][self.flow_num][1]["meta"]=="swich_flow":
                        self.level=1
                        self.flow_num=1
                        self.logger.info("switching flow")
                    elif self.call_flow["main_audios"][self.intent+"_"+str(self.level)][self.flow_num][1]["meta"]=="switch_flow_to_0":
                        self.level=0
                        self.flow_num=0
                        self.logger.info("switching flow")

                        
                if self.noise:
                    try:
                        self.audioplayback=True
                        self.send_audio(requests.get(self.call_flow["utils"]["inttrupt"]).content)
                        self.noise=False
                        self.logger.warning("noise detected")
                        self.noise_frames_count=0

                    except Exception as e:  
                        self.logger.error("audio playback failed beacause of {}".format(e))
                            
                

                self.long_silence=0    
                while self.long_silence<100:
                #self.logger.info("waiting for silence")
                    if self.call.connected:
                        sleep(.2)
                    else:
                            break
                if not self.call.connected:
                    break
                        
                self.logger.info("waiting for silence is over")

                self.long_silence=0

                try:
                    response=requests.post("http://172.16.1.209:5002/convert_{}".format(self.channel),data=self.combined_audio)
                    self.logger.error(response.text)
                    # m= self.convert_file(self.combined_audio)
                    # self.logger.info("audio file converted {}".format(m))
                    resp=json.loads(response.text)

                    threading.Thread(target=self.db_entry,args=(resp,mapping)).start()

                    if resp["transcribe"]=="":
                        x=self.read_wave_file(mapping["utils"][self.channel][1])
                        self.send_audio(x)
                    else:
                        self.combined_audio=b''
                        self.intent=resp["nlp"]["intent"]


                except Exception as e:
                    self.logger.error(e)
                    self.combined_audio=b''
                self.long_silence=0
                self.silent_frames_count=0



                # if resp["transcribe"]=="":
                #     self.level="cant_hear"
            # if self.level==0 and self.intent=="welcome" and self.channel=="en":
            #     if resp["transcribe"]:
            #         try:
            #             if  detect(resp["transcribe"]) != "en":


            #                 self.lang_change=True
            #         except Exception as e:
            #             self.logger.error("error occred while trying to change language {}".format(e))
        

        


            # if self.lang_change:
            #     self.channel="hi"
            #     self.logger.info("changing channel to hindi")
            #     self.lang_change=False

                # if self.level==1:
                #   self.level=2

                # elif self.level==2:
                #   while self.silent_frames_count<100:
                #         print("waiting")
                #         sleep(.01)
                # response=requests.post("http://65.2.152.189:5000/predict",data=self.combined_audio)
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

                # self.logger.info("audio length is "+str(self.read_length(mapping[self.channel][self.level])) + " seconds")
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

                #
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

            # convert data to json
            # response=requests.post("http://localhost:5005/convert",data=self.combined_audio)
            # self.logger.info(response.text)
        self.num_connected-=1
        update_data={"addr":"172.16.1.209"+":"+str(self.audiosocket.port),"update":{"conn":self.num_connected}}
        update_data=json.dumps(update_data)
        requests.put(self.call_api+"/update",update_data,headers=self.headers)

        print('Connection with {0} over'.format(self.call.peer_addr))

        return


def handel_call():

    audiosocket = Audiosocket(("0.0.0.0", 9000))
   
    while True:
        #audiosocket.prepare_output(outrate=8000, channels=2, ulaw2lin=True)
        #call = audiosocket.listen()
        stream = AudioStreamer(audiosocket)
        noise_stream = threading.Thread(target=stream.start_noise_detection)
        noise_stream.start()
        playback_stream = threading.Thread(target=stream.start_audio_playback, args=(mapping,))
        playback_stream.start()


handel_call()
