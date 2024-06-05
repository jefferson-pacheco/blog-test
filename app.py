from flask import Flask, jsonify, request, make_response
from appbanco import Autor, Postagem, app, db
import json
import jwt 
from datetime import datetime, timedelta 
from functools import wraps
# Rota padrão - GET https://localhost:5000

def token_obrigatorio(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Verificar se um token foi enviado
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'mensagem': 'Token não foi incluido!'}, 401)
        # Se temos um token, validar acesso consultando o BD
        try:
            resultado = jwt.decode(token,app.config['SECRET_KEY'])
            autor = Autor.query.filter_by(id_autor=resultado['id_autor']).first()
        except:
            return jsonify({'menssagem': 'Token è invalido'},401)
        return f(autor,*args,**kwargs)
    return decorated

@app.route('/login')
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('login invalido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatorio"'})
    usuario = Autor.query.filter_by(nome=auth.username).first()
    if not usuario:
        return make_response('login invalido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatorio"'})
    if auth.password == usuario.senha:
        token = jwt.encode({'id_autor': usuario.id_autor, 'exp':datetime.utcnow() + timedelta
                    (minutes=30)},app.config['SECRET_KEY'])
        return jsonify({'token':token})
    return make_response('login invalido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatorio"'})


@app.route('/autores')
def obter_autores():
    autores = Autor.query.all()
    lista_de_autores = []
    for autor in autores:
        autor_atual = {}
        autor_atual['id_autor'] = autor.id_autor
        autor_atual['nome'] = autor.nome
        autor_atual['email'] = autor.email
        lista_de_autores.append(autor_atual)

    return jsonify({'autores': lista_de_autores})

@app.route('/autores/<int:id_autor>', methods=['GET'])
def obter_autor_por_id(id_autor):
    autor = Autor.query.filter_by(id_autor=id_autor).first()
    if not autor:
        return jsonify(f'Autor não encontrado!')
    autor_atual = {}
    autor_atual['id_autor'] = autor.id_autor
    autor_atual['nome'] = autor.nome
    autor_atual['email'] = autor.email

    return jsonify(f'Voçè buscou pelo autor: {autor_atual}')

@app.route('/autores', methods=['POST'])
def novo_autor():
    novo_autor = request.get_json()
    autor = Autor(
        nome=novo_autor['nome'], senha=novo_autor['senha'], email=novo_autor['email'])
    
    db.session.add(autor)
    db.session.commit()

    return jsonify({'mensagem': 'Usuario criado com sucesso'}, 200)

@app.route('/autores/int:id_autor>', methods=['PUT'])
def alterar_autor(id_autor):
    usuario_a_alterar = request.get_json()
    autor = Autor.query.filter_by(id_autor=id_autor).first()
    if not autor:
        return jsonify({'mensagem': 'Este usuario não foi encontrado'})
    try:
        if usuario_a_alterar['nome']:
            autor.nome = usuario_a_alterar['nome']
    except:
        pass
    try:
        if usuario_a_alterar['email']:
            autor.email = usuario_a_alterar['email']
    except:
        pass
    try:
        if usuario_a_alterar['senha']:
            autor.senha = usuario_a_alterar['senha']
    except:
        pass

    db.session.commit()
    return jsonify({'mensagem': 'Usuario alterado com sucesso!'})


@app.route('/autores/<int:id_autor>', methods=['DELETE'])
def excluir_auor(id_autor):
    autor_existente = Autor.query.filter_by(id_autor=id_autor).first()
    if not autor_existente:
        return jsonify({'mensagem': 'Este autor nnão foi encontrado'})
    db.session.delete(autor_existente)
    db.session.commit()

    return jsonify({'mensagem': 'Autor excluido com sucesso!'})



app.run(port=5000, host='localhost', debug=True)