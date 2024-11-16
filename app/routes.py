from flask import request, jsonify
from app import app
from app.database import get_db_connection

@app.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in users])

@app.route('/user', methods=['POST'])
def add_user():
    new_user = request.json
    name = new_user['name']
    
    conn = get_db_connection()
    conn.execute('INSERT INTO users (name) VALUES (?)', (name,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'User added successfully!'}), 201
