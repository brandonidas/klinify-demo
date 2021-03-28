from flask import Flask, render_template, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from functools import wraps
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import yaml

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///klinify_users'
app.config['SECRET_KEY'] = 'demonstration'
db = SQLAlchemy(app)
CORS(app)


class Admin(db.Model):
    __tablename__ = "admin"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    password = db.Column(db.String(255))

    def __init__(self, name, password):
            self.name = name
            self.password = password

    def __repr__(self):
        return '%s/%s/' % (self.id, self.name)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    dob = db.Column(db.Date())
    updated_at = db.Column(db.DateTime())

    def __init__(self, name, dob):
        self.name = name
        self.dob = dob
        self.updated_at = datetime.now()

    def __repr__(self):
        return '%s/%s/%s/%s' % (self.id, self.name, self.dob, self.updated_at)


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):

        token = None

        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']

        if not token:
            return jsonify({'message': 'a valid token is missing'})

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_admin = Admin.query.filter_by(
                id=data['id']).first()
        except:
            return jsonify({'message': 'token is invalid'})

        return f(*args, **kwargs)
    return decorator


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})

    admin = Admin.query.filter_by(name=auth.username).first()

    if admin.password == auth.password: # TODO use password hash
        token = jwt.encode({'id': admin.id, 'exp' : datetime.utcnow() + timedelta(minutes=2)}, app.config['SECRET_KEY']) 
        return jsonify({'token' : token}) 
    return make_response('could not verify',  401, {'WWW.Authentication': 'Basic realm: "login required"'})

@app.route('/create', methods = ['POST'])
@token_required
def create_user():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            new_user = User(data['name'],data['dob'])
            db.session.add(new_user)
            db.session.commit()
            return jsonify({'status':'successful', 'data':data})
            
    return jsonify({'status':'unsuccessful'})


@app.route('/read_admins', methods = ['GET'])
@token_required
def read_adminss():
    if request.method == 'GET':
        data = Admin.query.order_by(Admin.id).all()
        data_json = []
        for i in range(len(data)):
            data_dict = {
                'id': str(data[i]).split('/')[0],
                'name': str(data[i]).split('/')[1],
            }
            data_json.append(data_dict)
        return jsonify(data_json)
    return jsonify({'status':'unsuccessful'})

@app.route('/read', methods = ['GET'])
@token_required
def read_users():
    if request.method == 'GET':
        data = User.query.order_by(User.id).all()
        data_json = []
        for i in range(len(data)):
            data_dict = {
                'id': str(data[i]).split('/')[0],
                'name': str(data[i]).split('/')[1],
                'dob': str(data[i]).split('/')[2],
                'updated_at': str(data[i]).split('/')[3],
            }
            data_json.append(data_dict)
        return jsonify(data_json)
    return jsonify({'status':'unsuccessful'})


@app.route('/<id>', methods = ['GET', 'DELETE', 'PUT'])
@token_required
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
        if del_data == None:
            return jsonify({'error':'no record found for id'})
        db.session.delete(del_data)
        db.session.commit()
        return jsonify({'status': 'user ID: '+id+' has been deleted'})
    elif request.method == 'PUT':
        if request.is_json:
            json_data = request.get_json()
            new_name =  json_data['name']
            db_data = User.query.filter_by(id=id).first()
            if db_data == None:
                return jsonify({'error':'no record found for id'})
            db_data.name = new_name
            db_data.updated_at = datetime.now()
            db.session.commit()
            return jsonify({'status': 'user ID: '+id+' has been updated'})
        else:
            return jsonify({'error':'request not in JSON'})
    return jsonify({'status':'unsuccessful'})

@app.route('/youngest/<n>', methods = ['GET'])
@token_required
def handle_n_youngest(n):
    if request.method == 'GET':
        data = User.query.order_by(User.id).all()
        data_json = []
        n = int(n)
        if n > len(data):
            return jsonify({'status':'unsuccessful'})

        for i in range(len(data)):
            data_dict = {
                'id': str(data[i]).split('/')[0],
                'name': str(data[i]).split('/')[1],
                'dob': date_helper(str(data[i]).split('/')[2])
            }
            data_json.append(data_dict)

        sorted_dicts = sorted(data_json , key=lambda k: k['dob'], reverse=False) 
        return jsonify(sorted_dicts[-int(n):])
    return jsonify({'status':'unsuccessful'})

def date_helper(date_string)->int:
    return int(date_string.replace('-', ''))
assert date_helper('2021-03-23') == 20210323

if __name__ == '__main__':
    app.run(debug=True)
