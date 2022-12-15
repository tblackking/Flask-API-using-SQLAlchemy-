from flask import Flask, jsonify, request, make_response
from api_with_db import Autor, Postagem, app, db
import json 
import jwt 
from datetime import datetime, timedelta
from functools import wraps 

def token_mandatory(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None 
        
        # Verificar se um token foi enviado
        if 'x-access-token' in request.headers: 
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'AUTH': 'Token nao foi incluido!'}, 401)
        
        # Se temos um token, validar acesso consultando o BD
        try:
            resultado = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            autor = Autor.query.filter_by(
                id_autor=resultado['id_autor']).first()
        except:
            return jsonify({'AUTH': 'Token INVALIDO'}, 401)
        return f(autor, *args, **kwargs)
    return decorated


@app.route('/login')
def login():
    auth = request.authorization 
    if not auth or not auth.username or not auth.password:
        return make_response({'AUTH': 'Login invalido'},
                             401,
                             {'WWW-Authenticate': 'Basic realm="Login OBRIGATORIO"'})

    usuario = Autor.query.filter_by(email=auth.username).first()
    if not usuario:
         return make_response({'AUTH': 'Login invalido'}, 
                              401,
                              {'WWW-Authenticate': 'Basic realm="Login OBRIGATORIO"'})
         
    if auth.password == usuario.senha:
        token = jwt.encode({'id_autor': usuario.id_autor, 'exp': datetime.utcnow() 
                            + timedelta(minutes=30)}, app.config['SECRET_KEY'])
        return jsonify({'TOKEN-JWT': token})
    
    return make_response({'AUTH': 'Login invalido'}, 
                              401,
                              {'WWW-Authenticate': 'Basic realm="Login OBRIGATORIO"'})
# POSTAGEM API

# DEFAULT ROUTE - GET http://localhost:5000
@app.route('/')
@token_mandatory
def obter_postagens(autor):
    postagens = Postagem.query.all()
    lista_de_postagem = []
    for postagem in postagens:
        postagem_atual = {}
        postagem_atual['titulo'] = postagem.titulo 
        postagem_atual['id_autor'] = postagem.id_autor 
        lista_de_postagem.append(postagem_atual)
        
    if len(lista_de_postagem) == 0:
        return jsonify({'ERROR': "Nao existem postagens no momento para leitura"}, 404)
    
    return jsonify({'postagens': lista_de_postagem})
       

# GET postagem for ID - GET http://localhost:5000/postagem/1 
@app.route('/postagem/<int:indice>', methods=['GET'])
@token_mandatory
def obter_postagem_por_indice(autor, id_postagem):
    postagens = Postagem.query.filter_by(id_postagem=id_postagem).first()
    postagem_atual = {}
    
    if not postagens:
        return jsonify({'ERROR': 'Postagem nao encontrada...'}, 404)
    
    
    try:
        postagem_atual['titulo'] = postagens.titulo
    except:
        pass
    
    postagem_atual['id_autor'] = postagens.id_autor
    
    return jsonify({'postagem': postagem_atual}) # FORMATAÇÃO   


# POST postagem - POST http://localhost:5000/postagem
@app.route('/postagem', methods=['POST'])
@token_mandatory
def nova_postagem(autor):
    try:
        
        novo_postagem = request.get_json()
        postagem = Postagem(titulo=novo_postagem['titulo'], id_autor=novo_postagem['id_autor'])
        
        db.session.add(postagem)
        db.session.commit()
        
        return jsonify({'INFO': 'Postagem criada com sucesso'}, 201)
        
    except:
        return jsonify({'ERROR': 'Valores inseridos nao permitidos'}, 401)
    

# Change postagem - PUT http://localhost:5000/postagem/1
@app.route('/postagem/<int:indice>', methods=['PUT'])
@token_mandatory
def alterar_postagem(autor, id_postagem):
    postagem_alterada = request.get_json()
    postagem = Postagem.query.filter_by(id_postagem=id_postagem).first()
    try:
        postagem.titulo = postagem_alterada['titulo']
    except:
        pass
    try:
        postagem.id_autor = postagem_alterada['id_autor']
    except:
        pass 
    
    db.session.commit()
    return jsonify({'INFO': 'Postagem alterada com sucesso'}, 204)


# Delete postagem - DELETE http://localhost:5000/postagem/1
@app.route('/postagem/<int:indice>', methods=['DELETE'])
@token_mandatory
def deletar_postagem(autor, id_postagem):
    postagem_a_ser_excluido = Postagem.query.filter_by(id_postagem=id_postagem).first()
    if not postagem_a_ser_excluido:
        return jsonify({'ERROR': 'Não foi encontrado uma postagem com este ID'}, 404)

    db.session.delete(postagem_a_ser_excluido)
    db.session.commit()

    return jsonify({'INFO': 'Postagem excluida com sucesso!'}, 204)




# AUTOR API
@app.route('/autores')
@token_mandatory
def obter_autores(autor):
    autores = Autor.query.all() # Extraindo dados da tabela
    lista_de_autores = [] 
    for autor in autores:
        autor_atual = {}
        autor_atual['id_autor'] = autor.id_autor
        autor_atual['nome'] = autor.nome
        autor_atual['email'] = autor.email 
        autor_atual['admin'] = autor.admin
        lista_de_autores.append(autor_atual)
        
    if len(lista_de_autores) == 0:
        return jsonify({'ERROR': "Nao existem postagens no momento para leitura"}, 404)
        
    return jsonify({'autores':lista_de_autores})
        
@app.route('/autores/<int:id_autor>', methods=['GET'])
@token_mandatory
def obter_autor_por_id(autor, id_autor):
    autor = Autor.query.filter_by(id_autor=id_autor).first()
    if not autor:
        return jsonify({'ERROR': 'Autor nao encontrado...'}, 404)

    autor_atual = {}
    autor_atual['id_autor'] = autor.id_autor
    autor_atual['nome'] = autor.nome
    autor_atual['email'] = autor.email
    
    return jsonify({'autor': autor_atual}) # FORMATAÇÃO   
    
@app.route('/autores', methods=['POST'])
@token_mandatory
def novo_autor(autor):
    try:
        novo_autor = request.get_json()
        autor = Autor(nome=novo_autor['nome'], email=novo_autor['email'], senha=novo_autor['senha'])
        
        db.session.add(autor)
        db.session.commit()
        
        return jsonify({'INFO': 'Usuario criado com sucesso'}, 200)
        
    except:
        return jsonify({'ERROR': 'Valores inseridos nao permitidos'}, 401)
    
    
        

@app.route('/autores/<int:id_autor>', methods=['PUT'])
@token_mandatory
def alterar_autor(autor, id_autor):
    autor_change = request.get_json()
    autor = Autor.query.filter_by(id_autor=id_autor).first()
    if not autor:
        return jsonify({'ERROR': 'Autor nao encontrado...'}, 404)
    
    try:
        if autor_change['nome']:
            autor.nome = autor_change['nome']
    except:
        pass 
    
    try:
        if autor_change['email']:
            autor.email = autor_change['email']
    except:
        pass 
    
    try:
        if autor_change['senha']:
            autor.email = autor_change['senha']
    except:
        pass
    
    db.session.commit()
    
    return jsonify({'INFO': f'Usuario {id_autor} alterado com sucesso!'})
    


@app.route('/autores/<int:id_autor>', methods=['DELETE'])
@token_mandatory
def excluir_autor(autor, id_autor):
    autor_existente = Autor.query.filter_by(id_autor=id_autor).first()
    if not autor_existente:
        return jsonify({'ERROR': 'Autor nao encontrado..'}, 404)
    db.session.delete(autor_existente)
    db.session.commit()
    
    return jsonify({'INFO': 'Autor excluido com sucesso!'})


    


app.run(port=5000, host='localhost', debug=True)
