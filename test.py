
from audiosocket import *


from mapping import *


from example_application_labels import AudioStreamer
import pyttsx3

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