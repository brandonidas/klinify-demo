from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import yaml
from datetime import datetime

app = Flask(__name__)
db_config = yaml.load(open('db.yaml'))
POSTGRES = {
    'user': '',
    'pw': '',
    'db': 'klinify_users',
    'host': 'localhost',
    'port': '5432',
}
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///klinify_users'

db = SQLAlchemy(app)
CORS(app)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    dob = db.Column(db.Date())
    updated_at = db.column(db.DateTime())

    def __init__(self, name, dob):
        self.name = name
        self.dob = dob

    def __repr__(self):
        return '%s/%s/%s' % (self.id, self.name, self.dob)


@app.route('/', methods=['GET', 'POST'])
def index():
    # if request.form:
    #     print(request.form)
    return render_template('home.html')

# Todo routes
# Create User POST
@app.route('/create', methods = ['POST'])
def create_user():
    if request.method == 'POST':
        print("in request")
        if request.is_json:
            print("in json")
            data = request.get_json()
            print(data)
            new_user = User(data['name'],data['dob'])
            db.session.add(new_user)
            db.session.commit()
            return data
            
    return render_template('create_user.html')
# Read all users 
# Read any single user
@app.route('/<id>')
def id(id):
    return id
# Update Name
# Delete a user via id

if __name__ == '__main__':
    app.run(debug=True)