from flask import Flask, request,jsonify
from flask_cors import CORS
from service.ingestion_data import ingest_data,print_query_results
import logging
from uuid import uuid4
from service.llm_call import llm_call
from werkzeug.utils import secure_filename
from service.detect_api import skyflow_identify, skyflow_detect
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("FlaskApp")
# Create an instance of the Flask class
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

app.config['UPLOAD_FOLDER'] = 'uploads'  # Folder to store uploaded files
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
# Define a route and its corresponding function
@app.route('/health')
def hello_world():
    logger.info('Health check called')
    return 'Hello, World! This is my first Flask application.'

@app.route('/ingest', methods=['POST'])
def ingest_data_file():
    req_id = str(uuid4())  # Generate a unique request ID
    logger.debug(f"Request ID {req_id}: Received new request")

     # Save uploaded files to the specified directory
    if 'files' not in request.files:
        return jsonify({'error': 'No files uploaded'}), 400

    files = request.files.getlist('files')
    auth_level = request.form.get("auth_level")
    uploaded_paths = []
    for file in files:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        uploaded_paths.append(file_path)

    # Ingest the uploaded files into the vector database using a separate service
    ingest_data(uploaded_paths,auth_level)
    return jsonify({'message': f'Files successfully uploaded and ingested', 'request_id': req_id}), 200

@app.route('/db_query', methods=['GET'])
def db_query():
    req_id = str(uuid4())  # Generate a unique request ID
    logger.debug(f"Request ID {req_id}: Received new request")
    data = request.json
    query = data.get('query')
    auth_level = data.get('auth_level')
    return jsonify(print_query_results(query,auth_level))

@app.route('/llm_call', methods=['GET'])
def send_query_llm():
    req_id = str(uuid4())  # Generate a unique request ID
    logger.debug(f"Request ID {req_id}: Received new request")
    data = request.json
    query = data.get('query')
    auth_level = data.get('auth_level')
    prompt = print_query_results(query,auth_level)
    if not prompt["results"]:
        response = {
            "error": "You don't have access to the answer to this question due to insufficient authorization level."
        }
    else:
        response = llm_call(prompt)

    return jsonify(response)

@app.route('/detect_check', methods=['GET'])
def send_text_detect():
    data = request.json
    text = data.get('text')
    tokenize_response = skyflow_detect(text)
    tokenize_text = tokenize_response['processed_text']
    re_identify_response = skyflow_identify(tokenize_text)
    re_identify_text = re_identify_response['text']
    response = {
     "tokenize_text": tokenize_text,
    "re_identify_text": re_identify_text
    }
    return jsonify(response)
# Run the Flask application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001,debug=True)