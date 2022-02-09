"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Todo
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user/<user_id>', methods=['GET'])
def handle_hello(user_id):
    user = User.query.get(user_id)
    return jsonify(user.serialize()), 200

@app.route("/user/register", methods=['POST'])
def create_user():
    body = request.get_json()
    new_user = User(email=body['email'], password=body['password'], is_active=True)
    print(new_user)
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.serialize()),200

@app.route("/todos", methods=['GET'])
def get_todos():
    todo_list = Todo.query.all()
    return jsonify([todo.serialize() for todo in todo_list]), 200

@app.route("/todos/print", methods=['POST'])
def print_todo():
    body = request.get_json()
    new_todo = Todo(label=body['label'], done=body['done'])
    print(new_todo)
    db.session.add(new_todo)
    db.session.commit()
    return jsonify(new_todo.serialize()), 200

@app.route("/todos/delete/<int:todo_id>", methods=['DELETE'])
def delete_todo(todo_id):
    Todo.query.filter_by(id=todo_id).delete()
    db.session.commit()
    return jsonify({}), 200


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
