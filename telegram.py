from flask import Flask, request, jsonify
import telebot
import threading

# Initialize Flask app
app = Flask(__name__)
chat_id=[]
# Initialize Telegram bot
bot = telebot.TeleBot("7144846540:AAGMzRZRmlV8NtQQfQ67vD5butARXFL4tCM")
@bot.message_handler(commands=['start'])
def handle_all_messages(message):
    global chat_id 
    chat_id.append(message.chat.id)
    bot.send_message(message.chat.id,"hi")

# Endpoint to receive audio file
@app.route('/send_audio', methods=['POST'])
def send_audio():
    # Extract data from the POST request
    data = request.get_json()
    
    # Extract chat ID and audio file from the request
    
    audio_file = data.get('path')
    global chat_id
    if chat_id:
        for i in chat_id:
    # Send audio file to the specified chat ID
            if chat_id and audio_file:
                x=open(audio_file)
                bot.send_audio(chat_id, x)
                x.close()

                return jsonify({'success': True, 'message': 'Audio sent successfully'})
            else:
                return jsonify({'success': False, 'message': 'Missing chat_id or audio in the request'})
    else:
        print("no chat id was found")

if __name__ == '__main__':
    
    bot.polling(none_stop=True)