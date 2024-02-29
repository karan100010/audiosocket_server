from flask import Flask, request, jsonify
import telebot
from asterisk.manager import Manager
import os
import threading
import requests
from pydub import AudioSegment
from io import BytesIO
import pymongo
from telebot import types
import wave
import random


manager = Manager()
manager.connect('localhost')
manager.login('karan', 'test')
chat_id=[]
# Initialize Telegram bot
conn= pymongo.MongoClient("mongodb+srv://root:toor@testcluster.exl8ah5.mongodb.net/Grievance?retryWrites=true&w=majority&appName=TestCluster",uuidRepresentation='standard')
bot = telebot.TeleBot("7144846540:AAGMzRZRmlV8NtQQfQ67vD5butARXFL4tCM")
def convert_file(file):
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
    
@bot.message_handler(commands=['start'])
def handle_all_messages(message):
    global chat_id 
    with open("chat_id.txt","+a") as file:
        file.write(str(message.chat.id) + '\n')
        file.close()

    bot.send_message(message.chat.id,"hi")

start_index=0
end_index=5
#write a handeler for menu options

@bot.message_handler(content_types=['voice'])
def handle_audio(update):
    #dounload the audio file from the user and save it in the server as wav file
    file = bot.get_file(update.voice.file_id)
    file_url = f"https://api.telegram.org/file/bot{bot.token}/{file.file_path}"
    response = requests.get(file_url)
    print(response.status_code)

    if response.status_code == 200:

       
# Assuming you have the OGG stream stored in a variable named ogg_stream

        # Create a BytesIO object to treat the stream as a file-like object
        ogg_stream_bytesio = BytesIO(response.content)

        # Load the OGG audio stream from the BytesIO object
        ogg_audio = AudioSegment.from_file(ogg_stream_bytesio, format="ogg")

        # Set the desired sample rate (8000Hz)
        desired_sample_rate = 8000

        # Resample the audio to 8000Hz
        ogg_audio = ogg_audio.set_frame_rate(desired_sample_rate).set_sample_width(2)

        # Export the audio as a WAV file
        ogg_audio.export("output.wav", format="wav")

    #merge audio file with header.wav file
    sound1 = AudioSegment.from_file("output.wav")
    sound2 = AudioSegment.from_file("demo_audios/en/header.wav")
    combined = sound2 + sound1
    combined = combined.set_frame_rate(desired_sample_rate).set_sample_width(2)

    
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

@bot.message_handler(commands=['get_all'])
def handle_menu(message):
    #send the user a list of menu options
    global start_index
    global end_index
    x=conn["Grievance"]["grievances"]

    lis=[i for i in x.find()]
    print(lis[0])
    for i in lis[start_index:end_index]:
        # markup = types.ReplyKeyboardMarkup(row_width=2)
        # itembtn1 = types.KeyboardButton("reply")
        # itembtn2 = types.KeyboardButton("forword")
        
                         

        # try:
        #     conn["Grievance"]["grievances"].update_one({"_id":str(i[_id])},{"$set":{"status":"in progress"}})

        # except:
        #     bot.send_message(message.chat.id,"error in updating status")

        bot.send_message(message.chat.id,str(i["transcript"]))
        bot.send_message(message.chat.id,str(i["categoryName"]))
        bot.send_message(message.chat.id,"open")
        
        file=convert_file(i["audio"])
        bot.send_audio(message.chat.id,open(file,"rb"))
        
        reply_markup = types.InlineKeyboardMarkup()
        reply_markup.add(types.InlineKeyboardButton("Reply", callback_data='reply'))
        bot.send_message(message.chat.id,"reply",reply_markup=reply_markup)
        
        reply_markup = types.InlineKeyboardMarkup()
        reply_markup.add(types.InlineKeyboardButton("open", callback_data='"mongo_id":{}'.format(str(i['_id']))))
        reply_markup.add(types.InlineKeyboardButton("in progress", callback_data='mongo_id:{}'.format(str(i['_id']))))
        reply_markup.add(types.InlineKeyboardButton("resolved", callback_data='mongo_id:{}'.format(str(i['_id']))))
        bot.send_message(message.chat.id,"pelase select an option if you want to change status",reply_markup=reply_markup)
    reply_markup = types.InlineKeyboardMarkup()
    reply_markup.add(types.InlineKeyboardButton("Next", callback_data='next'))
    bot.send_message(message.chat.id,"next",reply_markup=reply_markup)
    start_index+=5
    end_index+=5
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    data=call.data
    if data.startswith("mongo_id"):
        try:
            conn["Grievance"]["grievances"].update_one({"_id":data.split(":")[1]},{"$set":{"status":data.split(":")[1]}})
            bot.send_message(call.message.chat.id,"status updated")
        except Exception as e:
            bot.send_message(call.message.chat.id,"error in updating status")
            bot.send_message(call.message.chat.id,str(e))
    elif data.startswith("reply"):
        bot.send_message(call.message.chat.id, "Please record your reply now...")
    elif data.startswith("next"):
        global start_index
        global end_index
        x=conn["Grievance"]["grievances"]
        lis=[i for i in x.find()]

        if end_index>len(lis):
            end_index=len(lis)
        x=conn["Grievance"]["grievances"]
        lis=[i for i in x.find()]
        for i in x.find()[start_index:end_index]:
            reply_markup = types.InlineKeyboardMarkup()
            reply_markup.add(types.InlineKeyboardButton("Reply", callback_data='reply'))
            bot.send_message(call.message.chat.id,"reply",reply_markup=reply_markup)
            reply_markup.add(types.InlineKeyboardButton("open", callback_data='"mongo_id":{}'.format(str(i['_id']))))
            reply_markup = types.InlineKeyboardMarkup()
            reply_markup.add(types.InlineKeyboardButton("Reply", callback_data='reply'))
            reply_markup.add(types.InlineKeyboardButton("open", callback_data='"mongo_id":{}'.format(str(i['_id']))))
            reply_markup.add(types.InlineKeyboardButton("in progress", callback_data='mongo_id:{}'.format(str(i['_id']))))
            reply_markup.add(types.InlineKeyboardButton("resolved", callback_data='mongo_id:{}'.format(str(i['_id']))))
            bot.send_message(call.message.chat.id,"pelase select an option if you want to change status",reply_markup=reply_markup)

            bot.send_message(call.message.chat.id,str(i["transcript"]))
            file=convert_file(i["audio"])
            bot.send_audio(call.message.chat.id,open(file,"rb"))
            bot.send_message(call.message.chat.id,"reply",reply_markup=reply_markup)
        reply_markup = types.InlineKeyboardMarkup()
        reply_markup.add(types.InlineKeyboardButton("Next", callback_data='next'))
        start_index+=5
        end_index+=5


if __name__ == '__main__':
    
    poll=threading.Thread(target=bot.polling)
    poll.run()
