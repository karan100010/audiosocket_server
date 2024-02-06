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
from example_application_labels import AudioStreamer
import pyttsx3
import io
import os

# stream=AudioStreamer()
# while stream.conn.connected:
#     data=stream.conn.read()
#     req={"audiofile":base64.b64encode(data).decode('utf-8')}
#     requests.post("http://localhost:5000/audio",json=req)

def text_to_speech(text):
    # Convert text to speech using a text-to-speech library
    # Store the speech in a byte-sized object with ulaw encoding
    # Return the byte-sized object
    
    # Example code using pyttsx3 library
   
    # Initialize the text-to-speech engine
    engine = pyttsx3.init()
    
    # Set the ulaw encoding

    
    # Create a byte-sized object to store the speech
    
    # Save the speech to the byte-sized object
    engine.save_to_file(text, "temp.wav")
    
    # Run the text-to-speech engine
    engine.runAndWait()
    
   #read "temp.wav" as a byte-sized object
    with open("temp.wav", "rb") as file:
        speech = file.read()
    
    return speech

# Example usage
for language in nlp_mapping:
    for key in nlp_mapping[language]:
  
        speech=text_to_speech(nlp_mapping[language][key])
        if not os.path.exists("demo_audios/"+language+"/"+str(key)+".wav"):
          with open("demo_audios/"+language+"/"+str(key)+".wav","wb") as file:
              file.write(speech)