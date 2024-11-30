from flask import request, jsonify
from app import app
import re
import os
from app.azureUtils import get_blob_service_client, upload_file_to_blob, download_file_from_blob, upload_file_path_to_blob
from app.database import get_db_connection
from app.crowdCounting import annotate_and_count
from ultralytics import YOLO

localFileDir = '/localFiles'
connection_str = app.config['AZURE_STORAGE_CONNECTION_STRING']
container_name = app.config['AZURE_STORAGE_CONTAINER']
blob_service_client = get_blob_service_client(connection_str)

def replace_az_docker(url: str) -> str:
    if len(url) == 0:
        return url
    regex = r"^http://azuriteDocker:10000/"
    pattern = re.compile(regex)
    if pattern.search(url):
        return pattern.sub("http://localhost:10000/", url)
    return url

@app.after_request
def handle_options(response):
    response.access_control_allow_credentials = True
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-Requested-With"
    return response

@app.route('/archive', methods=['GET'])
def get_all_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT cc.*, m.name as model_name
            FROM crowdCounting cc
            LEFT JOIN models m ON cc.model_id = m.id
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        # Convert rows to list of dictionaries
        data = []
        for row in rows:
            data.append({
                'id': row['id'],
                'original_url': replace_az_docker(row['original_url']),
                'annotated_url': replace_az_docker(row['annotated_url']),
                'averageCountPerFrame': row['averageCountPerFrame'],
                'model_name': row['model_name']
            })
        
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": "Failed to fetch data from database: " + str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        file_url = upload_file_to_blob(file, container_name, blob_service_client)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO crowdCounting (original_url, annotated_url, averageCountPerFrame)
            VALUES (?, ?, ?)
        ''', (file_url, '', 0.0))
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
    except Exception as e:
        return jsonify({"error": "Failed to insert into database: " + str(e)}), 500

    return jsonify({"id": last_id, "url": replace_az_docker(file_url)}), 200

@app.route('/count/<int:id>', methods=['PUT'])
def count(id):
    data = request.json
    model_id = data.get("model_id")

    if not model_id:
        return jsonify({"error": "Model id is required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT id, name FROM models WHERE id = ?', (model_id,))
        model = cursor.fetchone()

        if model is None:
            conn.close()
            return jsonify({"error": "Model not found"}), 404
    
        model_name = model['name']
        model_path = f"/backend/models/{model_name}.pt"
        
        if not os.path.exists(model_path):
            conn.close()
            return jsonify({"error": f"Model file {model_path} not found"}), 404
        
        loaded_model = YOLO(model_path)

        cursor.execute('SELECT id, original_url FROM crowdCounting WHERE id = ?', (id,))
        record = cursor.fetchone()

        if record is None:
            conn.close()
            return jsonify({"error": "Record not found"}), 404
        remote_url = record['original_url']

        if not remote_url:
            conn.close()
            return jsonify({"error": "Original file not found"}), 404
        
        download_path = download_file_from_blob(remote_url, blob_service_client, localFileDir, container_name)
        average_count, output_path = annotate_and_count(loaded_model, input_path=download_path)
        annotated_url = upload_file_path_to_blob(output_path, container_name, blob_service_client)
        cursor.execute('''
            UPDATE crowdCounting
            SET annotated_url = ?, averageCountPerFrame = ?, model_id = ?
            WHERE id = ?
        ''', (replace_az_docker(annotated_url), average_count, model_id, id))
        conn.commit()

        cursor.execute('SELECT id, annotated_url FROM crowdCounting WHERE id = ?', (id,))
        updated_row = cursor.fetchone()
        conn.close()

        if updated_row is None:
            return jsonify({"error": "Failed to fetch updated record"}), 404

        return jsonify({"id": updated_row['id'], "url": updated_row['annotated_url']}), 200
    except Exception as e:
        return jsonify({"error": "Failed to count: " + str(e)}), 500

@app.route('/models', methods=['GET'])
def get_model_names():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM models')
        rows = cursor.fetchall()
        conn.close()
        
        models = [{'id': row['id'], 'name': row['name']} for row in rows]
        
        return jsonify(models), 200
    except Exception as e:
        return jsonify({"error": "Failed to fetch model names from database: " + str(e)}), 500
    
@app.route('/get/<int:id>', methods=['GET'])
def get(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT id, original_url, annotated_url, averageCountPerFrame FROM crowdCounting WHERE id = ?', (id,))
        record = cursor.fetchone()

        if record is None:
            conn.close()
            return jsonify({"error": "Record not found"}), 404

        data = {
            'id': record['id'],
            'original_url': replace_az_docker(record['original_url']),
            'annotated_url': replace_az_docker(record['annotated_url']),
            'averageCountPerFrame': record['averageCountPerFrame']
        }

        conn.close()
        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
