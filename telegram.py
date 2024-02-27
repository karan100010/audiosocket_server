from flask import Flask, request, jsonify
import telebot
import threading
from astrisk.manager import Manager
import os

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
def handle_audio(update, context):
    #dounload the audio file from the user and save it in the server as wav file
    file = bot.getFile(update.message.voice.file_id)
    file.download('demo_audios/en/audio.wav')
    #merge audio file with header.wav file
    os.system("sox -m demo_audios/en/header.wav demo_audios/en/audio.wav -r 8000 demo_audios/en/output.wav && chmod 700 demo_audios/en/output.wav")

    manager.originate(
        channel="SIP/zoiper",
        context="my-phones",
        exten="500",  # Assuming Zoiper is extension 100
        priority=1,
        caller_id="CallerID <caller_id_number>",
        timeout=30000,  # Timeout in milliseconds
        #async=True  # Perform asynchronously
        application="Playback",
        data="output"
        
    )
    #play audio file for the user when the call is answered


if __name__ == '__main__':
    
    poll=threading.Thread(target=bot.polling)
    poll.run()
