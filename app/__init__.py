from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')
CORS(app)

from app import routes
