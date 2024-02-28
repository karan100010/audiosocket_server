from flask import Flask, request, jsonify
import telebot
from asterisk.manager import Manager
import os
import threading
import requests
from pydub import AudioSegment
from io import BytesIO


manager = Manager()
manager.connect('localhost')
manager.login('karan', 'test')
chat_id=[]
# Initialize Telegram bot
bot = telebot.TeleBot("7144846540:AAGMzRZRmlV8NtQQfQ67vD5butARXFL4tCM")
@bot.message_handler(commands=['start'])
def handle_all_messages(message):
    global chat_id 
    with open("chat_id.txt","+a") as file:
        file.write(str(message.chat.id) + '\n')
        file.close()

    bot.send_message(message.chat.id,"hi")

@bot.message_handler(content_types=['voice'])
def handle_audio(update):
    #dounload the audio file from the user and save it in the server as wav file
    file = bot.get_file(update.voice.file_id)
    file_url = f"https://api.telegram.org/file/bot{bot.token}/{file.file_path}"
    response = requests.get(file_url)

    if response.status_code == 200:

       
# Assuming you have the OGG stream stored in a variable named ogg_stream

        # Create a BytesIO object to treat the stream as a file-like object
        ogg_stream_bytesio = BytesIO(response.content)

        # Load the OGG audio stream from the BytesIO object
        ogg_audio = AudioSegment.from_file(ogg_stream_bytesio, format="ogg")

        # Set the desired sample rate (8000Hz)
        desired_sample_rate = 8000

        # Resample the audio to 8000Hz
        ogg_audio = ogg_audio.set_frame_rate(desired_sample_rate)

        # Export the audio as a WAV file
        ogg_audio.export("output.wav", format="wav")


    
    #merge audio file with header.wav file
    sound1 = AudioSegment.from_file("output.wav")
    sound2 = AudioSegment.from_file("demo_audios/en/header.wav")
    combined = sound2 + sound1
    
    combined.export("final.wav", format='wav')
    #chmod final.wav file to 777
    os.system("chmod 777 final.wav")

   
    manager.originate(
        channel="SIP/zoiper",
        context="my-phones",
        exten="500",  # Assuming Zoiper is extension 100
        priority=1,
        caller_id="CallerID <caller_id_number>",
        timeout=30000,  # Timeout in milliseconds
        #async=True  # Perform asynchronously
        application="Playback",
        data="/home/vboxuser/audiosocket_server/final"
        
    )
    #play audio file for the user when the call is answered


if __name__ == '__main__':
    
    poll=threading.Thread(target=bot.polling)
    poll.run()
