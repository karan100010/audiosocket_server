import telebot
bot_api_token="7144846540:AAGMzRZRmlV8NtQQfQ67vD5butARXFL4tCM"
bot2= telebot.TeleBot(bot_api_token)
@bot2.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    audio = open('test2.wav', 'rb') 
    bot2.send_audio(message.chat.id,audio)
    audio.close()
bot2.polling()
