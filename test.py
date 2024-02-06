
from audiosocket import *
from mapping import *
import pyttsx3
import os

# stream=AudioStreamer()
# while stream.conn.connected:
#     data=stream.conn.read()
#     req={"audiofile":base64.b64encode(data).decode('utf-8')}
#     requests.post("http://localhost:5000/audio",json=req)

def text_to_speech(text,path):
    # Convert text to speech using a text-to-speech library
    # Store the speech in a byte-sized object with ulaw encoding
    # Return the byte-sized object
    
    # Example code using pyttsx3 library
   
    # Initialize the text-to-speech engine
    engine = pyttsx3.init()
    
    # Set the ulaw encoding

    
    # Create a byte-sized object to store the speech
    
    # Save the speech to the byte-sized object
    engine.save_to_file(text, path)

    engine.runAndWait()
    

    
   #read "temp.wav" as a byte-sized object
 
    return True

# Example usage
for language in nlp_mapping:
    for key in nlp_mapping[language]:
  
       
        if not os.path.exists("demo_audios/"+language+"/"+str(key)+".wav"):
            text_to_speech(nlp_mapping[language][key],"demo_audios/"+language+"/"+str(key)+".wav")
            print("demo_audios/"+language+"/"+str(key)+".wav")