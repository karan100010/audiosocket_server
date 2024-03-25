import wave
import os
import asyncio
import pandas as pd
import requests
import time
import threading
import threading
def read_wave_file(filename):
    #self.logger.debug("Reading wave file")
    with wave.open(filename, 'rb') as wave_file:
      audio = wave_file.readframes(wave_file.getnframes())
    return audio

iters= 1
def send_file(audio):
   start_time = time.time()
   response=requests.post("http://172.16.1.209:5002/convert_en",data=audio)
   response_time = time.time() - start_time
   return response_time
def combined(filename):
    audio=read_wave_file(filename)
    response_time=send_file(audio)
    df=df.append({"response_time":response_time,"file_name":filename},ignore_index=True)
    print("response time for {} is {}".format(filename,response_time))
    return
   
df=pd.DataFrame(columns=["response_time","file_name"])
threads = []
for i in range(iters):
    for i in os.listdir("demo_audios/resp"):
        response_time=threading.Thread(target=combined,args=("demo_audios/resp/"+i,)).start()
        threads.append(response_time)
        time.sleep(1)
for thread in threads:
    thread.join()
    
print(df)
df.to_csv("test.csv")
print("testing done")