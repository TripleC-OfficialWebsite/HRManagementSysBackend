from flask import Blueprint, Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from pymongo import ReturnDocument
import requests



projectAPI = Blueprint('project_api', __name__, url_prefix='/pro')

folder_link = "https://drive.google.com/drive/folders/1ZM4M2DewwVOPLVmPuMX7aN97_MXoYmnR"

# do not change
folder_id = folder_link.split("/")[-1]
api_key = 'AIzaSyB7Rvjg9mV1HnFVsSnalkD2cQw_z4bScio'
url = f'https://www.googleapis.com/drive/v3/files?q=%27{folder_id}%27+in+parents+and+trashed%3Dfalse&key={api_key}'

# Create a new client and connect to the server
client = MongoClient("mongodb+srv://root:28GJiZtTYasykeil@cluster0.4lirrab.mongodb.net/?retryWrites=true&w=majority", tls=True,
                             tlsAllowInvalidCertificates=True)
db = client.manageSys
project_collection = db.member

CORS(projectAPI)
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

@projectAPI.route("/project_photo/<string:title>", methods=["get"])
def get_photos(title):
    response = get(title)
    if response.status_code == 404:
        return jsonify({'error': f'project {title} not found'}), 404
    
    filenames = set(response.get_json()[0]['picture'])


    response = requests.get(url)
    files = response.json().get('files', [])
    
    if not files:
        return jsonify({'error': 'No files found'}), 404
    
    result = []    
    for file in files:
        if file["name"] in filenames:
            link = f'https://drive.google.com/uc?id={file["id"]}'
            result.append({file["name"]: link})
    
    if result:
        return jsonify(result)
    else:
        return jsonify({'error': 'No matching files found'}), 404


@projectAPI.route("/project/<string:title>/<string:active_type>", methods=["GET"])
def get(title=None, active_type="active"):
    if title:
        query = {"title": title, "type": active_type}
        project = project_collection.find_one(query, {"_id": 0})

        if project:
            return jsonify([project])
        
        return jsonify({'error': f'project {project} not found'}), 404
    else:
        data = list(project_collection.find({"type": active_type}, {"_id": 0}))
        return jsonify(data)
    
@projectAPI.route("/project_add", methods=["POST"])
def add_project():
    data = request.get_json()
    title = data['title']
    if title is None:
        return jsonify({'error': 'Missing project title'}), 400
    query = {'title': title}
    update = {'$set': {key: value for key, value in data.items() if key != 'title'}}

    project = project_collection.find_one_and_update(query, update, upsert=True, \
                                                   return_document=ReturnDocument.AFTER)
    project_id = str(project['_id'])

    return jsonify({'_id': project_id, 'status_code': 0})

@projectAPI.route('/project_delete/<string:title>', methods=['DELETE'])
def remove_member(title):
    if title is None:
        return jsonify({'error': 'Missing input fullname'}), 400
    
    query = {'title': title}
    result = project_collection.delete_one(query)
    
    if result.deleted_count == 1:
        return jsonify({'success': f'Project {title} deleted successfully'}), 200

    return jsonify({'error': f'Project {title} not found'}), 404
