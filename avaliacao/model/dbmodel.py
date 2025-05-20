from sqlalchemy import Column, Integer, String, DateTime, Boolean
from model.db import Base
from flask_login import UserMixin

class Usuario(UserMixin, Base):
    __tablename__ = 'usuario'
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    senha = Column(String)
    nome = Column(String)
    tel = Column(String, unique=True)

    def __init__(self, email=None, senha=None,nome=None,tel=None):
        self.email = email
        self.senha = senha
        self.nome = nome
        self.tel = tel       

class Contato(Base):
    __tablename__ = 'contato'
    id = Column(Integer, primary_key=True)
    email = Column(String)
    tel = Column(String)
    nome = Column(String)
    id_dono = Column(Integer)
    
    
    def __init__(self, email=None, tel=None, nome=None, id_dono=None):
        self.email = email
        self.tel = tel
        self.nome = nome
        self.id_dono = id_dono


class Mensagem(Base):
    __tablename__ = 'mensagem'
    id = Column(Integer, primary_key=True)
    titulo = Column(String)
    texto = Column(String)
    id_emitente = Column(Integer)
    id_destino = Column(Integer)
    dt_envio = Column(DateTime)
    lida = Column(Boolean, default=False)

    def __init__(self, titulo=None,texto=None, id_emitente=None, id_destino=None, dt_envio=None):
        self.titulo = titulo
        self.texto = texto
        self.id_emitente = id_emitente
        self.id_destino = id_destino
        self.dt_envio = dt_envio