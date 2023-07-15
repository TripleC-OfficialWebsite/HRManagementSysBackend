from flask import Flask, request,jsonify
from flask_cors import CORS
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
# from admin import adminAPI
# from member import memberAPI
import admin
import member
import project
import requests

# imports for google drive api

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
CREDENTIALS_FILE = 'Credential.json'

app = Flask(__name__)

app.register_blueprint(admin.adminAPI)
app.register_blueprint(member.memberAPI)
app.register_blueprint(project.projectAPI)


uri = "mongodb+srv://root:28GJiZtTYasykeil@cluster0.4lirrab.mongodb.net/?retryWrites=true&w=majority"

# app = Flask(__name__)
CORS(app)

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'), tls=True,
                             tlsAllowInvalidCertificates=True)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


db = client.manageSys
test = db.test

# member_collection = db['member']
collections = {'admin':admin.admin_collection,'member':member.member_collection,'project':project.project_collection}

# get photos with filename
@app.route("/photo", methods=["get"])
def get_photo():
    filename = request.args.get('filename')

    # do not change
    folder_id = '18TIDcCxduEub6ysnNYmSflEKoldtzn7f'
    api_key = 'AIzaSyB7Rvjg9mV1HnFVsSnalkD2cQw_z4bScio'
    url = f'https://www.googleapis.com/drive/v3/files?q=%27{folder_id}%27+in+parents+and+trashed%3Dfalse&key={api_key}'

    response = requests.get(url)
    files = response.json().get('files', [])

    if not files:
        return jsonify({'error': 'No file found'}), 404

    else:
        for file in files:
            if (file["name"] == filename):
                link = f'https://drive.google.com/uc?id={file["id"]}'
                # link = f'https://drive.google.com/file/d/{file["id"]}/view'
                return jsonify([{filename: link}])
        return jsonify({'error': f'{filename} not found'}), 404


@app.route("/", methods=["GET"])
def get():
    data = []
    collection = request.args.get('collection')
    if (collection == None):
        for c in collections.values():
            for document in c.find({}, {"_id": 0}):
                data.append(document)
        return jsonify(data)
        
    for document in collections[collection].find({}, {"_id": 0}):
        data.append(document)
    return jsonify(data)

## clear database
@app.route("/collection_clear", methods=["DELETE"])
def collection_clear():
    collection_name = request.args.get('collection')
    if collection_name not in collections:
        return jsonify({'error': 'Invalid Collection Name'}), 401
    else:
        if collections[collection_name].count_documents({}) == 0:
            return jsonify({'success': f'Collection {collection_name} already cleared'})
        collections[collection_name]. delete_many({})
        return jsonify({'success': f'Collection {collection_name} cleared successfully'})



if __name__ == "__main__":
    app.run(debug=True)
    