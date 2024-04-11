from flask import Flask, request, jsonify
import requests
from pymongo import MongoClient

from datetime import datetime, UTC


# CONSTANTS

# define the base URL for the audio files
AUDIO_URL_BASE = "http://172.16.1.209:7000"
AUDIO_URL_DOWNLOAD_BASE = "http://172.16.1.209:8000/"
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DB = 'tts_db'
MONGO_COLLECTION = 'audio_metadata'


# create a MongoClient instance
client = MongoClient(MONGO_HOST, MONGO_PORT)

# connect to the database
client = client[MONGO_DB]

# connect to the collection
collection = client[MONGO_COLLECTION]

# create a Flask app
app = Flask(__name__)


@app.route('/audios', methods=['GET'])
def get_all():
    """
    Get all the audio files from the database

    Returns:
    dict: A list of all the audio files in the database
    """
    try:
        # get all the documents from the collection
        documents = collection.find({})
        # create a list to store the documents
        docs = []
        # iterate over the documents
        for doc in documents:
            # remove the _id field from the document
            doc.pop('_id')
            # append the document to the list
            docs.append(doc)
        # return the list of documents as a JSON response
        return {'audios': docs}, 200
    except Exception as e:
        return {'error': str(e)}, 500


@app.route('/audios/<audio_identifier>', methods=['GET'])
def get_one(audio_identifier):
    """
    Get a single audio file from the database

    Args:
    audio_identifier (str): The unique identifier of the audio file

    Returns:
    dict: The audio file as a dictionary
    """
    try:
        # get the document from the collection
        document = collection.find_one({'audio_identifier': audio_identifier})
        if document is None:
            return {'error': 'No audio found with the given audio_identifier'}, 404
        # remove the _id field from the document
        document.pop('_id')
        # return the document as a JSON response
        return document, 200
    except Exception as e:
        return {'error': str(e)}, 500


@app.route('/audios', methods=['POST'])
def synthesize_audio():
    """
    Synthesizes an audio file and saves it to the database

    Body Params:
    text (str): The text to synthesize
    msisdn (str): The MSISDN of the user
    voiceCode (str): The voice code to use
    speech_rate (int): The speech rate to use
    use_stress (bool): Whether to use stress
    quality (str): The quality of the audio
    voiceCode (str): The voice code to use
    audio_identifier (str): The unique identifier of the audio file

    Returns:
    dict: The result of the operation    
    """
    try:
        # get text from body
        body = request.get_json()
        if 'text' not in body:
            return {'error': 'Text not found in request body'}

        if 'msisdn' not in body:
            return {'error': 'MSISDN not found in request body'}

        if 'voiceCode' not in body:
            return {'error': 'Voice code not found in request body'}

        if 'speech_rate' not in body:
            return {'error': 'Speech rate not found in request body'}

        if 'use_stress' not in body:
            return {'error': 'Use stress not found in request body'}

        if 'quality' not in body:
            return {'error': 'Quality not found in request body'}

        if 'voiceCode' not in body:
            return {'error': 'Voice code not found in request body'}

        if 'audio_identifier' not in body:

            return {'error': 'Audio identifier not found in request body'}

        check = collection.find_one(
            {"audio_identifier": body["audio_identifier"]})

        if check:
            return {'error': 'Audio identifier already exists'}, 409

        # send a request to the text-to-speech API
        response = requests.post(
            f"{AUDIO_URL_BASE}/synthesize", json=body)

        # check if the request was successful
        if response.status_code != 200:
            return {'error': 'Failed to synthesize audio'}

        # get the audio file from the response
        audio = response.json()

        if 'error' in audio:
            return {'error': audio['error']}

        # # DUMMY RESPONSE FROM THE API
        # audio = {
        #     'message': 'success',
        #     'msisdn': body['msisdn'],
        #     'status': 200
        # }

        audio["audio_url"] = AUDIO_URL_DOWNLOAD_BASE + audio["msisdn"] + ".wav"
        audio["text"] = body["text"]
        audio["msisdn"] = body["msisdn"]
        audio["voiceCode"] = body["voiceCode"]
        audio["speech_rate"] = body["speech_rate"]
        audio["use_stress"] = body["use_stress"]
        audio["quality"] = body["quality"]
        audio["voiceCode"] = body["voiceCode"]
        audio["audio_identifier"] = body["audio_identifier"]

        current_time = datetime.now(UTC)
        audio["created_at"] = current_time
        audio["updated_at"] = current_time

        # save the audio file to the database
        collection.insert_one(audio)
        # print(audio)
        res = {"status": "success"}
        return jsonify(res), 200

    except Exception as e:
        print(e)
        return {'error': str(e)}, 500


@app.route('/audios/<audio_identifier>', methods=['PATCH'])
def update_audio(audio_identifier):
    """
    Update an audio file in the database

    Args:
    audio_identifier (str): The unique identifier of the audio file

    Body Params:
    text (str): The text to synthesize (optional)
    msisdn (str): The MSISDN of the user (optional)
    voiceCode (str): The voice code to use (optional)
    speech_rate (int): The speech rate to use (optional)
    use_stress (bool): Whether to use stress (optional)
    quality (str): The quality of the audio (optional)
    voiceCode (str): The voice code to use (optional)
    audio_identifier (str): The unique identifier of the audio file (optional)

    Returns:
    dict: The result of the operation
    """

    try:
        # get the document from the collection
        document = collection.find_one({'audio_identifier': audio_identifier})
        if document is None:
            return {'error': 'No audio found with the given audio_identifier'}, 404
        # get the updated fields from the request body
        body = request.get_json()
        # update the document with the new fields
        collection.update_one({'audio_identifier': audio_identifier}, {
            '$set': body})
        # return a success message
        return {'status': 'success'}, 200
    except Exception as e:
        return {'error': str(e)}, 500


@app.route('/audios/<audio_identifier>', methods=['DELETE'])
def delete_audio(audio_identifier):
    """
    Delete an audio file from the database

    Args:
    audio_identifier (str): The unique identifier of the audio file

    """

    try:
        # get the document from the collection
        document = collection.find_one({'audio_identifier': audio_identifier})
        if document is None:
            return {'error': 'No audio found with the given audio_identifier'}, 404
        # remove the _id field from the document
        document.pop('_id')
        # return the document as a JSON response
        collection.delete_one({'audio_identifier': audio_identifier})
        return {'status': 'success'}, 204
    except Exception as e:
        return {'error': str(e)}, 500


if __name__ == '__main__':
    app.run()
