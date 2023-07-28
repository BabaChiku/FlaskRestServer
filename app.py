from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Create a Todo model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    completed = db.Column(db.Boolean, default=False)

    def __init__(self, title, description, completed=False):
        self.title = title
        self.description = description
        self.completed = completed

# Create a Todo Schema/Serializer
class TodoSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'description', 'completed')

todo_schema = TodoSchema()
todos_schema = TodoSchema(many=True)


# Create a Todo
@app.route('/todo', methods=['POST'])
def add_todo():
    title = request.json['title']
    description = request.json['description']
    new_todo = Todo(title, description)

    db.session.add(new_todo)
    db.session.commit()

    return todo_schema.jsonify(new_todo)

# Get all Todos
@app.route('/todo', methods=['GET'])
def get_todos():
    all_todos = Todo.query.all()
    result = todos_schema.dump(all_todos)
    return jsonify(result)

# Get a single Todo by ID
@app.route('/todo/<int:id>', methods=['GET'])
def get_todo(id):
    todo = Todo.query.get(id)
    if not todo:
        return jsonify({'message': 'Todo not found'}), 404
    return todo_schema.jsonify(todo)

# Update a Todo
@app.route('/todo/<int:id>', methods=['PUT'])
def update_todo(id):
    todo = Todo.query.get(id)
    if not todo:
        return jsonify({'message': 'Todo not found'}), 404
    title = request.json.get('title', todo.title)
    description = request.json.get('description', todo.description)
    completed = request.json.get('completed', todo.completed)

    todo.title = title
    todo.description = description
    todo.completed = completed

    db.session.commit()

    return todo_schema.jsonify(todo)

# Delete a Todo
@app.route('/todo/<int:id>', methods=['DELETE'])
def delete_todo(id):
    todo = Todo.query.get(id)
    if not todo:
        return jsonify({'message': 'Todo not found'}), 404
    db.session.delete(todo)
    db.session.commit()

    return todo_schema.jsonify(todo)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)