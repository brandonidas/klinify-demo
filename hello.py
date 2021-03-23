from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import yaml

app = Flask(__name__)
db_config = yaml.load(open('db.yaml'))
print(db_config)

@app.route('/')
def hello_world():
    return 'Hello, World!'
