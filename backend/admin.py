from flask import Blueprint
from flask import Flask, request,jsonify
from flask_cors import CORS
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
# from app import collections

adminAPI = Blueprint('admin_api', __name__, url_prefix='/admin')

uri = "mongodb+srv://root:28GJiZtTYasykeil@cluster0.4lirrab.mongodb.net/?retryWrites=true&w=majority"

# app = Flask(__name__)
CORS(adminAPI)

# # Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'), tls=True,
                             tlsAllowInvalidCertificates=True)
db = client.manageSys
admin_collection = db['admin']

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# db = client.manageSys
test = admin_collection

@adminAPI.route("/get", methods=["GET"])
def get():
    data = []
    for document in test.find({}, {"_id": 0}):
        data.append({
            "username": document["username"],
            "password": document["password"]
        })
    return jsonify(data)
@adminAPI.route('/admin_delete', methods=['DELETE'])
def removeAdmin():
    key = request.args.get('username')
    if not key:
        return jsonify({'error': 'Missing username'}), 400
    query = {'username': key}
    result = test.delete_one(query)
    if result.deleted_count == 1:
        return jsonify({'success': f'Admin {key} deleted successfully'}), 200
    else:
        return jsonify({'error': f'Admin {key} not found'}), 404
    
@adminAPI.route('/admin_validate', methods=['GET'])
def validateAdmin():
    key = request.args.get('username')
    value = request.args.get('password')
    if not key or not value:
        return jsonify({'error': 'Missing username or password'}), 400
    query = {'username': key,'password': value}
    admin = test.find_one(query)
    if not admin:
        return jsonify({'error': 'Invalid username or password'}), 401
    else:
        admin["_id"] = str(admin["_id"])
        return jsonify(admin), 200

@adminAPI.route("/admin_add", methods=["POST"])
def addAdmin():
    key = request.args.get('username')
    value = request.args.get('password')
    data = {'username': key,'password': value}
    if (test.find_one(data) != None):
        return jsonify({'error': 'Admin is already in the admin collection', 'status_code': 1})
    test.insert_one(data)
    member = test.find_one(data)
    member_id = str(member['_id'])
    return jsonify({'_id': member_id, 'status_code': 0})

