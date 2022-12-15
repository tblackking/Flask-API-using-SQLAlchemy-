from flask import Flask 
from flask_sqlalchemy import SQLAlchemy 
import os

# GET PATH THAT FILE
basedir = os.path.abspath(os.path.dirname(__file__))
    
# Create FLASK API
app = Flask(__name__)

with app.app_context():
    # Create SQLAlchemy instance 
    app.config['SECRET_KEY'] = 'A2#DFSAab212!!@341'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')

    # Instance SQLAlchemy
    db = SQLAlchemy(app)
    db: SQLAlchemy  # Tipando o tipo da variavel db

    # Define table POST structure
    # id_postagem, titulo, autor 

    class Postagem(db.Model):
        __tablename__ = 'postagem'
        id_postagem = db.Column(db.Integer, primary_key=True)
        titulo = db.Column(db.String)
        #nome_autor = db.Column(db.String, db.ForeignKey('autor.nome'))
        id_autor = db.Column(db.Integer, db.ForeignKey('autor.id_autor'))
        # Extrair um valor da TABELA A para usar na TABELA B

    # Define table AUTOR structure 
    # id_autor, nome, email, senha, admin, postagens

    class Autor(db.Model):
        __tablename__ = 'autor'
        id_autor = db.Column(db.Integer, primary_key=True) # primary_key afirma que vai sempre ser gerado um numero
        nome = db.Column(db.String)                        # dinamicamente 
        email = db.Column(db.String)
        senha = db.Column(db.String)
        admin = db.Column(db.Boolean)
        postagens = db.relationship('Postagem') # Relacionar com outra TABELA


def iniciar_banco():
    # Execute command to build database
    db.drop_all() # Exclui o que tiver de valor relacionado a essa tabela
    db.create_all() # Cria tudo que foi setado


    # # Create administrator user
    administrator = Autor(nome='Black King', 
                        email='blackking_ever@gmail.com', 
                        senha='F@c1l@1234#', 
                        admin=True)
    db.session.add(administrator)
    db.session.commit()


if __name__ == "__main__":
    with app.app_context():
        iniciar_banco()
