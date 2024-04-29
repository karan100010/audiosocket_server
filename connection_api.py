
from flask import Flask, request, jsonify
import pymongo
import json

with open("db.txt") as f:
       data=f.read()
if data.endswith("\n"):
    data=data.strip("\n")
print(data)

app = Flask(__name__)

try:
    conn = pymongo.MongoClient(data)
    print("Connected successfully!!!")
except:
    print("Could not connect to MongoDB")
@app.route('/min_connetions', methods=['GET'])
def min_connections():
    # connection = conn['test']['connections']
    try:
        
    #     #run minima fuction on the num_connected field
    #     min_value_document = connection.find_one({}, sort=[("field_name", 1)])
        return jsonify("172.16.1.209:9000")
    except Exception as e:
        return jsonify("Error in getting data because "+str(e))
    
@app.route('/api/connections/decider/<id>', methods=['GET'])
def get_decider(id):
    connection = conn['test']["calls"]
    try:
        connection_data = connection.find({"call_id": id})
        #run minima fuction on the num_connected field
        # get decision form the data
        resp={}
        for i in connection_data:
            resp["hangup"]=i["hangup"]
            resp["transfer"]=i["transfer"]
            return jsonify(resp)
    except Exception as e:
        return jsonify("Error in getting data because "+str(e))

@app.route('/api/connections', methods=['POST'])
def create_connection():
    connection = conn['test']['connections']
    data_dict = request.get_json()
    

    try:
        connection_id = connection.insert_one(data_dict)
        print("sucessfully inserted connection data")
    except Exception as e:
        return jsonify("Error in inserting data becuase "+str(e))    
    return jsonify(str(connection_id.inserted_id))


@app.route('/api/connections/update', methods=['PUT'])
def update_connection():
    connection = conn['test']['connections']
    data = request.get_json()
    connection_id = data['addr']

    try:
        connection.update_one({'addr': connection_id}, {'$set': {list(data["update"].keys())[0]:data["updates"][list(data["update"].keys())[0]]}})
        print("sucessfully updated connection data")
    except:
        return jsonify("Error in updating data")


@app.route('/api/connections/delete', methods=['DELETE'])
def delete_connection():
    connection = conn['test']['connection']
    data = request.data
    connection_id = data['connection_id']
    try:
        connection.delete_one({'_id': connection_id})
        print("sucessfully deleted connection data")
    except:
        return jsonify("Error in deleting data")
@app.route('/api/connections/get_free', methods=['GET'])

#calls apis start here 
    
@app.route('/api/connections/calls', methods=['POST'])
def add_call():
    connection = conn['test']["calls"]
    data = request.json
    print(data)

    try:
        connection.insert_one(data)
        print("sucessfully inserted call data")
    except Exception as e:
        return jsonify("Error in inserting data due to "+str(e))
    
    
# @app.route('/api/connections/calls/<id>', methods=['GET'])
# def get_call(id):
#     connection = conn['test']["calls"]
#     try:
#         connection_data = connection.find({'connection_id': id})
#         return jsonify(list(connection_data))
#     except:
#         return jsonify("Error in getting data")

#see all calls
@app.route('/api/connections/calls', methods=['GET'])
def get_calls():
    connection = conn['test']["calls"]
    try:
        connection_data = connection.find()
        return jsonify(list(connection_data))
    except:
        return jsonify("Error in getting data")

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5011, debug=True)    

