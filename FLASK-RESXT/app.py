from flask import Flask, Response, request, current_app, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restx import Api, Resource, fields
import json

from datetime import datetime
import jwt

import os.path
basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'storage.db')
app.config['SECRET_KEY'] = 'secret'

db = SQLAlchemy(app)#from app import db    db.create_all()
migrate = Migrate(app, db)#flask db init | migrate | upgrade

api = Api(app)

class Book(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    title=db.Column(db.String(80),nullable=False)
    author=db.Column(db.String(40),nullable=False)
    date_added=db.Column(db.DateTime(),default=datetime.utcnow)

    def __repr__(self):
        return self.title

book_model=api.model(
    'Book',
    {
        'id':fields.Integer(),
        'title':fields.String(),
        'author':fields.String(),
        'date_joined':fields.String(),
    }
)

@api.route('/books')
class Books(Resource):
    def get(self):
        return jsonify(
            {"books-get": 
                [
                {"id": 1, "title": "Book 1"},
                {"id": 2, "title": "Book 2"}
                ]
            }
        )
    def post(self):
        return jsonify(
            {"books-post": 
                [
                {"id": 1, "title": "Book 1"},
                {"id": 2, "title": "Book 2"}
                ]
            }
        )

@api.route('/books/<int:id>')
class Books(Resource):
    def get(self, id):
        return jsonify(
            {"books-get": 
                [
                {"id": 1, "title": "Book 1"},
                {"id": 2, "title": "Book 2"}
                ]
            }
        )
    def put(self, id):
        return jsonify(
            {"books-put": 
                [
                {"id": 1, "title": "Book 1"},
                {"id": 2, "title": "Book 2"}
                ]
            }
        )
    def delete(self, id):
        return jsonify(
            {"books-delete": 
                [
                {"id": 1, "title": "Book 1"},
                {"id": 2, "title": "Book 2"}
                ]
            }
        )

if __name__ == "__main__":
    app.run(debug=True)