from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from models import db, Author, Book

app = Flask(__name__)

# Налаштування для Flask і JWT
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['JWT_SECRET_KEY'] = 'key'
db.init_app(app)
jwt = JWTManager(app)

# Створення таблиць бази даних перед першим запитом
@app.before_first_request
def create_tables():
    db.create_all()

# Логін для створення токену
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if username != 'admin' or password != 'password':
        return jsonify({"msg": "Bad username or password"}), 401
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)

# Захищений ендпоінт для доступу тільки з валідним JWT токеном
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

# Додавання нового автора
@app.route('/author', methods=['POST'])
@jwt_required()
def add_author():
    name = request.json.get('name', None)
    if name:
        new_author = Author(name=name)
        db.session.add(new_author)
        db.session.commit()
        return jsonify({"msg": f"Author {name} added."}), 201
    return jsonify({"msg": "Name is required"}), 400

# Додавання нової книги
@app.route('/book', methods=['POST'])
@jwt_required()
def add_book():
    title = request.json.get('title', None)
    author_id = request.json.get('author_id', None)
    if title and author_id:
        new_book = Book(title=title, author_id=author_id)
        db.session.add(new_book)
        db.session.commit()
        return jsonify({"msg": f"Book {title} added."}), 201
    return jsonify({"msg": "Title and author_id are required"}), 400

if __name__ == '__main__':
    app.run(debug=True)
