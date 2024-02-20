from flask import Flask, request, jsonify
import telebot
import threading

chat_id=[]
# Initialize Telegram bot
bot = telebot.TeleBot("7144846540:AAGMzRZRmlV8NtQQfQ67vD5butARXFL4tCM")
@bot.message_handler(commands=['start'])
def handle_all_messages(message):
    global chat_id 
    with open("chat_id.txt","+a") as file:
        file.write(message.chat.id + '\n')

    bot.send_message(message.chat.id,"hi")


if __name__ == '__main__':
    
    poll=threading.Thread(target=bot.polling)
    poll.run()
