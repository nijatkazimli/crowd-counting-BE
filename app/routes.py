from flask import request, jsonify
from app import app
from app.azureUtils import get_blob_service_client, upload_file_to_blob
from app.database import get_db_connection

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    connection_str = app.config['AZURE_STORAGE_CONNECTION_STRING']
    container_name = app.config['AZURE_STORAGE_CONTAINER']

    blob_service_client = get_blob_service_client(connection_str)
    try:
        file_url = upload_file_to_blob(file, container_name, blob_service_client)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"file_url": file_url}), 200