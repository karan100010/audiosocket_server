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

iters= 100
resp_lis=[]
file_lis=[]
def send_file(audio):
   start_time = time.time()
   response=requests.post("http://172.16.1.209:5002/convert_en",data=audio)
   response_time = time.time() - start_time
   return response_time
def combined(file_lis,resp_lis,filename):
    audio=read_wave_file(filename)
    response_time=send_file(audio)
    resp_lis.append(response_time)
    file_lis.append(filename)

  
    print("response time for {} is {}".format(filename,response_time))
    print(len(resp_lis))
    return
   
df=pd.DataFrame(columns=["response_time","file_name"])
threads = []
for i in range(iters):
    for i in os.listdir("demo_audios/resp"):
        response_time=threading.Thread(target=combined,args=(file_lis,resp_lis,"demo_audios/resp/"+i,))
        response_time.start()
        threads.append(response_time)

for thread in threads:
    if thread:
        thread.join()
if len(resp_lis)!=iters*3:
    time.sleep(1)
    print("waiting for all threads to complete")
df["response_time"]=resp_lis
df["file_name"]=file_lis
print(df.describe())
df.to_csv("test.csv")
print("testing done")