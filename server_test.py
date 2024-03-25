import wave
import os
import asyncio
import pandas as pd
import requests
import time
import threading
def read_wave_file(filename):
    #self.logger.debug("Reading wave file")
    with wave.open(filename, 'rb') as wave_file:
      audio = wave_file.readframes(wave_file.getnframes())
    return audio

iters= 10 
def send_file(audio):
   start_time = time.time()
   response=requests.post("http://172.16.1.209:5002/convert_en",data=audio)
   response_time = time.time() - start_time
   return response_time
def combined(filename):
    audio=read_wave_file(filename)
    response_time=send_file(audio)
    df=df.append({"response_time":response_time,"file_name":filename},ignore_index=True)
    return
   
df=pd.DataFrame(columns=["response_time","file_name"])
for i in range(iters):
    for i in os.listdir("demo_audios/resp"):
        response_time=threading.Thread(target=combined,args=("demo_audios/resp/"+i,)).start()
        time.sleep(1)
df.to_csv("test.csv")
print("testing done")