from pymongo import MongoClient
from bson.json_util import dumps
from flask import Flask, request, jsonify
app=Flask(__name__)

def connect_to_mongodb(username, password, host, port, database_name):
    # Connection URI with authentication
    if username == "" and password == "":
        uri = f"mongodb://{host}:{port}/{database_name}"
    uri = f"mongodb://{username}:{password}@{host}:{port}/{database_name}"
    client = MongoClient(uri)
    return client
def create_collections(client, collection_name):

    collection = db[collection_name]
    return collection
# create post request handelr
FlaskApp = Flask(__name__)
@FlaskApp.route('/create', methods=['POST'])
def create(collection):
    #use bson data for binary data
    try:
        data = request.get_json()
        #insert data into collection
        collection.insert_one(data)
        return jsonify({'message': 'Data inserted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)})
    

# crate a put request handler
@FlaskApp.route('/update', methods=['PUT'])
def update(collection):
    try:
        data = request.get_json()
        #update data into 
        #use find_one to see the data
        collection.find_one({'_id': data['_id']})
        collection.update_one({'_id': data['_id']}, {'$set': data})
        return jsonify({'message': 'Data updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)})

# create a get request handler
    
@FlaskApp.route('/read', methods=['GET'])
def read(collection):
    try:
        data = collection.find()
        return dumps(data)
    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    client = connect_to_mongodb('', '', '', 27017, 'test')
    collection = create_collections(client, 'test')
    app.run(host='0.0.0.0', port=5008)
