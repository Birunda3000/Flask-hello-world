from unicodedata import name
from flask import Flask,jsonify,request, Response
import json
from flask_restx import Api, Resource,fields
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime, timedelta
import jwt
from flask_migrate import Migrate

basedir=os.path.dirname(os.path.realpath(__file__))

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir,'users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SQLALCHEMY_ECHO']=True
app.config['SECRET_KEY'] = 'secret'

db = SQLAlchemy(app)#from app import db    db.create_all()
migrate = Migrate(app, db)#flask db init | migrate | upgrade

api=Api(app, doc='/docs',title="A user API",description="A simple REST API for users")


from functools import wraps
def jwt_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = None
        if 'authorization' in request.headers:
            token = request.headers['authorization']
        if not token:
            return gera_response(403, "token", {}, "Token não informado")
        if 'Bearer' not in token:
            return gera_response(401, "token", {}, "Token inválido")    
        try:
            token_pure = token.replace('token_key ', '')
            decoded = jwt.decode(token_pure, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(decoded['id'])#just search for the user with the id
        except:
            return gera_response(403, "token", {}, "Token inválido, por erro")
        return f(current_user=current_user, *args, **kwargs)
    return wrapper


def gera_response(status, nome_do_conteudo, conteudo, mensagem=False):
    body = {}
    body[nome_do_conteudo] = conteudo

    if(mensagem):
        body["mensagem"] = mensagem

    return Response(json.dumps(body), status=status, mimetype="application/json")


class User(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    password=db.Column(db.String(100))
    description=db.Column(db.Text)
    date_added=db.Column(db.DateTime(),default=datetime.utcnow)
    #date_modified=db.Column(db.DateTime(),default=datetime.utcnow)
    def __repr__(self):
        return self.name

user_model=api.model(
    'User',
    {
        'id':fields.Integer(),
        'name':fields.String(),
        'password':fields.String(),
        'description':fields.String(),
        'date_joined':fields.String(),
    }
)

@api.route('/users')
class Users(Resource):

    @api.marshal_list_with(user_model,code=200,envelope="users")
    def get(self):
        ''' Get all users '''
        users=User.query.all()
        return users

    @api.marshal_with(user_model,code=201,envelope="user")
    @api.doc(params={'name:str':'The name of the user','password:str':'The password','description:str':'The description of the user'},body=user_model,responses={201:'User created!'})
    def post(self):
        ''' Create a new user '''
        data=request.get_json()

        name = data.get('name')
        password = data.get('password')
        description = data.get('description')
        datetime_ = datetime.utcnow()

        new_user=User(name=name, password=password, description=description, date_added=datetime_)

        db.session.add(new_user)

        db.session.commit()

        return new_user


@api.route('/user/<int:id>')
class UserResource(Resource):

    @api.marshal_with(user_model,code=200,envelope="user")
    @api.doc(params={'id:int':'The user id'},responses={201:'User created!'})
    def get(self,id):

        ''' Get a user by id '''
        user=User.query.get_or_404(id)

        return user

    @api.marshal_with(user_model,envelope="user",code=200)
    @api.doc(params={'name:str':'The name of the user','password:str':'The password','description:str':'The description of the user'},body=user_model,responses={201:'User updated!'})
    def put(self,id):

        ''' Update a user'''
        user_to_update=User.query.get_or_404(id)

        data=request.get_json()

        user_to_update.name=data.get('name')
        user_to_update.password=data.get('password')
        user_to_update.description=data.get('description')

        db.session.commit()

        return user_to_update,200

    @api.marshal_with(user_model,envelope="user_deleted",code=200)
    @api.doc(params={'id:int':'The user id'},responses={201:'User deleted!'})
    def delete(self,id):
        '''Delete a user'''
        user_to_delete=User.query.get_or_404(id)

        db.session.delete(user_to_delete)

        db.session.commit()

        return user_to_delete,200

user_model_login=api.model(
    'User_login',
    {
        'token':fields.String(),
    }
)

@api.route('/login/<int:id>')
class Login(Resource):

    @api.marshal_with(user_model_login,code=200,envelope="login_token")
    @api.doc(params={'id:int':'The user id'},responses={200:'Token generated!'})
    def get(self,id):
        ''' Get a auth token '''
        user=User.query.get_or_404(id)
        data=request.get_json()
        name = data.get('name')
        password = data.get('password')

        user = User.query.filter_by(name=name).first()

        if user and user.password == password:

            payload = {
                'id': user.id,
                'nome': user.name,
                'exp': datetime.utcnow() + timedelta(minutes=10)
                }
            token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
            return {'token': token}, 200
            #return gera_response(200, "token", {'token': token}, "Login efetuado com sucesso")
        else:
            return {'token': 'null'}, 401

# Rota protegida
@app.route("/protected", methods=["GET","POST"])
@jwt_required
def protected(current_user=None):
    return gera_response(200, "Logado", {},"Logado com sucesso em uma rota protegida")


if __name__ == "__main__":
    app.run(debug=True)