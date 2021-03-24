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
    updated_at = db.Column(db.DateTime()) # TODO forgot about this

    def __init__(self, name, dob):
        self.name = name
        self.dob = dob
        self.updated_at = datetime.now()

    def __repr__(self):
        #return '%s/%s/%s' % (self.id, self.name, self.dob)
        return '%s/%s/%s/%s' % (self.id, self.name, self.dob, self.updated_at)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('home.html')

# TODO: error handling
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
            return jsonify({'status':'successful', 'data':data})
            
    return render_template('create_user.html')


@app.route('/read', methods = ['GET'])
def read_users():
    print('here')
    if request.method == 'GET':
        data = User.query.order_by(User.id).all()
        data_json = []
        for i in range(len(data)):
            print(data[i])
            data_dict = {
                'id': str(data[i]).split('/')[0],
                'name': str(data[i]).split('/')[1],
                'dob': str(data[i]).split('/')[2],
                'updated_at': str(data[i]).split('/')[3],
            }
            data_json.append(data_dict)
        return jsonify(data_json)

@app.route('/<id>', methods = ['GET', 'DELETE', 'PUT'])
def id_handler(id):
    if request.method == 'GET':
        data = User.query.get(id)
        data_dict = {
            'id': str(data).split('/')[0],
            'name': str(data).split('/')[1],
            'dob': str(data).split('/')[2]
        }
        return jsonify(data_dict)
    elif request.method == 'DELETE':
        del_data = User.query.filter_by(id=id).first()
        db.session.delete(del_data)
        db.session.commit()
        return jsonify({'status': 'user ID: '+id+' has been deleted'})
    elif request.method == 'PUT':
        if request.is_json:
            json_data = request.get_json()
            new_name =  json_data['name']
            db_data = User.query.filter_by(id=id).first()
            if db_data.name == None:
                return jsonify({'error':'no record found for id'})
            db_data.name = new_name
            db_data.updated_at = date.now()
            db.session.commit()
            return jsonify({'status': 'user ID: '+id+' has been updated'})
        else:
            return jsonify({'error':'request not in JSON'})

# implement a list action. 
# List should take in a number n as a GET parameter that returns n youngest customers ordered by date of birth.
@app.route('/youngest/<n>', methods = ['GET'])
def handle_n_youngest(n):
    if request.method == 'GET':
        data = User.query.order_by(User.id).all()
        data_json = []
        print(data)

        # TODO rework with lambda
        for i in range(len(data)):
            data_dict = {
                'id': str(data[i]).split('/')[0],
                'name': str(data[i]).split('/')[1],
                'dob': date_helper(str(data[i]).split('/')[2])
            }
            data_json.append(data_dict)

        sorted_dicts = sorted(data_json , key=lambda k: k['dob'], reverse=False) 
        return jsonify(sorted_dicts[-int(n):]) # TODO not working... using a sorting algo or something else


def date_helper(date_string)->int:
    return int(date_string.replace('-', ''))
assert date_helper('2021-03-23') == 20210323

if __name__ == '__main__':
    app.run(debug=True)