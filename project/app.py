from flask import Flask, Response, request, current_app, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import json

import datetime
import jwt

import os.path
basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'storage.db')
app.config['SECRET_KEY'] = 'secret'

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    nome = db.Column(db.String(50))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))

    def to_json(self):
        return {"id": self.id, "nome": self.nome, "email": self.email}



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
            token_pure = token.replace('Bearer ', '')
            decoded = jwt.decode(token_pure, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = Usuario.query.get(decoded['id'])#just search for the user with the id
        except:
            return gera_response(403, "token", {}, "Token inválido, por erro")
        return f(current_user=current_user, *args, **kwargs)
    return wrapper



# Selecionar Tudo
@app.route("/usuarios", methods=["GET"])
def seleciona_usuarios():
    usuarios_objetos = Usuario.query.all()
    usuarios_json = [usuario.to_json() for usuario in usuarios_objetos]

    return gera_response(200, "usuarios", usuarios_json)

# Selecionar Individual
@app.route("/usuario/<id>", methods=["GET"])
def seleciona_usuario(id):
    usuario_objeto = Usuario.query.filter_by(id=id).first()
    usuario_json = usuario_objeto.to_json()

    return gera_response(200, "usuario", usuario_json)

# Cadastrar
@app.route("/usuario", methods=["POST"])
def cria_usuario():
    body = request.get_json()

    try:
        usuario = Usuario(nome=body["nome"], email= body["email"], password= body["password"])
        db.session.add(usuario)
        db.session.commit()
        return gera_response(201, "usuario", usuario.to_json(), "Criado com sucesso")
    except Exception as e:
        print('Erro', e)
        return gera_response(400, "usuario", {}, "Erro ao cadastrar")

# Atualizar
@app.route("/usuario/<id>", methods=["PUT"])
def atualiza_usuario(id):
    usuario_objeto = Usuario.query.filter_by(id=id).first()
    body = request.get_json()

    try:
        if('nome' in body):
            usuario_objeto.nome = body['nome']
        if('email' in body):
            usuario_objeto.email = body['email']
        
        db.session.add(usuario_objeto)
        db.session.commit()
        return gera_response(200, "usuario", usuario_objeto.to_json(), "Atualizado com sucesso")
    except Exception as e:
        print('Erro', e)
        return gera_response(400, "usuario", {}, "Erro ao atualizar")

# Deletar
@app.route("/usuario/<id>", methods=["DELETE"])
def deleta_usuario(id):
    usuario_objeto = Usuario.query.filter_by(id=id).first()

    try:
        db.session.delete(usuario_objeto)
        db.session.commit()
        return gera_response(200, "usuario", usuario_objeto.to_json(), "Deletado com sucesso")
    except Exception as e:
        print('Erro', e)
        return gera_response(400, "usuario", {}, "Erro ao deletar")

# Rota Login
@app.route("/login", methods=["POST"])
def login():
    body = request.get_json()
    email = body["email"]
    password = body["password"]

    usuario_objeto = Usuario.query.filter_by(email=email).first()

    if(usuario_objeto):
        if(usuario_objeto.password == password):
            
            payload = {
                'id': usuario_objeto.id,
                'nome': usuario_objeto.nome,
                'email': usuario_objeto.email,
                'iat': datetime.datetime.utcnow(),
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
            }

            token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
            return gera_response(200, "token", token, "Login realizado com sucesso")
        else:
            return gera_response(400, "usuario", {}, "Senha incorreta")
    else:
        return gera_response(400, "usuario", {}, "Usuário não encontrado") 

# Rota protegida
@app.route("/protected", methods=["POST"])
@jwt_required
def protected(current_user=None):
    return gera_response(200, "Logado", {},"Logado com sucesso em uma rota protegida")

def gera_response(status, nome_do_conteudo, conteudo, mensagem=False):
    body = {}
    body[nome_do_conteudo] = conteudo

    if(mensagem):
        body["mensagem"] = mensagem

    return Response(json.dumps(body), status=status, mimetype="application/json")

if __name__ == "__main__":
    app.run(debug=True)