from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from model.db import db_session, init_db
from model.dbmodel import *
import hashlib
import secrets
import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secrets.token_hex(16)


login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)
    
    
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['password']
        erros = []
        hash = ''
        if len(email) < 1:
            erros.append('Digite um email')
        elif email.find('@') == -1:
            erros.append('Email inválido')

        if len(senha) < 1:
            erros.append('Digite a senha')
        
        Usuario.query.all()
        user = Usuario.query.filter(Usuario.email == email).first()
        
        hash = hashlib.sha256(senha.encode('utf-8')).hexdigest()        

        if user == None or user.senha != hash:
            erros.append('Cadastro não encontrado')            

        if len(erros) > 0:
            return render_template('login.html', erros=erros, email=email)
        else:
            login_user(user)
            return redirect(url_for('home'))    
    return render_template('login.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        senha = request.form['password']
        senha2 = request.form['confirmPassword']
        celular = request.form['celular']
        erros = []

        if len(name) < 3:
            erros.append('Nome deve ter pelo menos 3 caracteres')
        if '@' not in email:
            erros.append('Email inválido')
        if len(senha) < 6:
            erros.append('Senha deve conter no mínimo 6 caracteres')
        if senha != senha2:
            erros.append('As senhas devem ser iguais')
        if len(celular) != 11:
            erros.append('Número inválido (11 dígitos com DDD)')

        if Usuario.query.filter(Usuario.email == email).first():
            erros.append('Email já cadastrado')
        if Usuario.query.filter(Usuario.tel == celular).first():
            erros.append('Telefone já cadastrado')

        if erros:
            return render_template('signup.html', erros=erros,name=name,email=email,celular=celular)
        
        hash = hashlib.sha256(senha.encode('utf-8')).hexdigest()
        novo_usuario = Usuario(email=email, senha=hash, nome=name, tel=celular)
        
        db_session.add(novo_usuario)
        db_session.commit()

        flash('Cadastro realizado com sucesso! Faça login.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/home')
@login_required
def home():
    contatos = Contato.query.filter(Contato.id_dono == current_user.id)
    return render_template('home.html', contatos=contatos, nome=current_user.nome)
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/novoContato', methods=['GET','POST'])
@login_required
def novoContato():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        tel = request.form['celular']
        erros = []

        if len(nome) < 3:
            erros.append('Nome deve ter pelo menos 3 caracteres')
        if email.find('@') == -1:
            erros.append('Email inválido')
        if len(tel) != 11:
            erros.append('Número inválido')
        
        if len(erros) > 0:
            return render_template('novoContato.html', erros=erros, nome=nome, email=email,celular=tel)
        else:
            contato = Contato(email=email,tel=tel,nome=nome,id_dono=current_user.id)
            db_session.add(contato)
            db_session.commit()
            
            return redirect(url_for('home'))        

    return render_template('novoContato.html')

@app.route('/editaContato/<int:id_contato>', methods=['GET','POST'])
@login_required
def editaContato(id_contato):
    erros = []

    contato = db_session.query(Contato).filter_by(id=id_contato).first()
    
    if contato.id_dono != current_user.id:
        erros.append('Acesso negado a esse contato')
        contatos = Contato.query.filter(Contato.id_dono == current_user.id)
        return render_template('home.html', contatos=contatos, erros=erros)

    if request.method == 'POST':
        email = request.form['email']
        name = request.form['nome']
        celular = request.form['celular']

        if len(name) < 3:
            erros.append('Nome deve ter pelo menos 3 caracteres')
        if email.find('@') == -1:
            erros.append('Email inválido')
        if len(celular) != 11:
            erros.append('Número inválido')

        if len(erros) > 0:
            return render_template('editaContato.html', erros=erros, contato=contato)
        
        contato.nome = name
        contato.email = email
        contato.tel = celular

        db_session.commit()
        return redirect(url_for('home'))
        

    return render_template('editaContato.html', contato=contato) 

@app.route('/mensagem/<int:id_contato>',  methods=['GET','POST'])
@login_required
def mensagem(id_contato):
    erros = []
    contato = db_session.query(Contato).filter_by(id=id_contato).first()
    
    if contato.id_dono != current_user.id:
        erros.append('Acesso negado a esse contato')
        contatos = Contato.query.filter(Contato.id_dono == current_user.id)
        return render_template('home.html', contatos=contatos, erros=erros)   
    


    if request.method == 'POST':
        titulo = request.form['titulo']
        texto = request.form['texto']
        id_emitente = current_user.id
        destino = Usuario.query.filter(Usuario.email == contato.email).first()

        if destino == None:
            erros.append('Usuario nao encontrado')
            return render_template('mensagem.html', erros=erros, nome=contato.nome, titulo=titulo, texto=texto)

        if id_emitente == destino.id:
            erros.append('Impossível enviar mensagem para você mesmo')
        
        if len(titulo) < 3:
            erros.append('Titulo deve ter pelo menos 3 caracteres')

        if len(texto) < 1:
            erros.append('Digite uma mensagem para enviar')

        if len(erros) > 0:
            return render_template('mensagem.html', erros=erros, nome=contato.nome, titulo=titulo, texto=texto) 

        mensagem = Mensagem(titulo=titulo,texto=texto, id_emitente=id_emitente, id_destino=destino.id,dt_envio=datetime.datetime.now())
        db_session.add(mensagem)
        db_session.commit()

        return render_template('mensagem.html', nome=contato.nome)

    return render_template('mensagem.html', nome=contato.nome)

@app.route('/mensagensRecebidas')
@login_required
def mensagensRecebidas():
    mensagens = Mensagem.query.filter(Mensagem.id_destino == current_user.id).order_by(Mensagem.dt_envio.desc()).all()
    
    mensagensComRemetente = []
    for msg in mensagens:
        remetente = Usuario.query.get(msg.id_emitente)
        mensagensComRemetente.append({
            'id': msg.id,
            'titulo': msg.titulo,
            'texto': msg.texto,
            'remetente': remetente.nome if remetente else "Remetente desconhecido",
            'data': msg.dt_envio.strftime('%d/%m/%Y %H:%M'),
            'lida': msg.lida
        })
    
    return render_template('mensagensRecebidas.html', mensagens=mensagensComRemetente)

def contarMensagensNaoLidas():
    if current_user.is_authenticated:
        return Mensagem.query.filter(Mensagem.id_destino == current_user.id, Mensagem.lida == False).count()
    return 0

@app.route('/marcarComoLida/<int:id_mensagem>')
@login_required
def marcarComoLida(id_mensagem):
    mensagem = Mensagem.query.filter(Mensagem.id==id_mensagem).first()

    if mensagem.id_destino != current_user.id:
        flash('Você não tem permissão para esta ação', 'danger')
        return redirect(url_for('mensagensRecebidas'))
    
    mensagem.lida = True
    db_session.commit()
    flash('Mensagem marcada como lida', 'success')
    return redirect(url_for('mensagensRecebidas'))



@app.route('/responderMensagem/<int:id_mensagem>', methods=['GET', 'POST'])
@login_required
def responderMensagem(id_mensagem):
    mensagemOriginal = Mensagem.query.filter(Mensagem.id == id_mensagem).first()
    erros = []

    if mensagemOriginal == None:
        flash('Não foi possivel encontrar a mensagem original')
        return redirect(url_for('mensagensRecebidas'))
    
    if mensagemOriginal.id_destino != current_user.id and mensagemOriginal.id_emitente != current_user.id:
        flash('Você não tem permissão para responder esta mensagem', 'danger')
        return redirect(url_for('home'))
    
    if mensagemOriginal.id_emitente == current_user.id:
        destinatario = Usuario.query.get(mensagemOriginal.id_destino)
    else:
        destinatario = Usuario.query.get(mensagemOriginal.id_emitente)
    
    if request.method == 'POST':
        titulo = request.form['titulo']
        texto = request.form['texto']
    
        if len(titulo) < 3:
            erros.append('Título deve ter pelo menos 3 caracteres')
        if len(texto) < 1:
            erros.append('Digite uma mensagem para enviar')
        
        if len(erros) > 0:
            return render_template('mensagem.html', nome=destinatario.nome,titulo=titulo,texto=texto,erros=erros)
        
        novaMensagem = Mensagem(titulo=titulo,texto=texto,id_emitente=current_user.id,id_destino=destinatario.id,dt_envio=datetime.datetime.now())
        
        db_session.add(novaMensagem)
        db_session.commit()
        
        flash('Resposta enviada com sucesso!', 'success')
        return redirect(url_for('mensagensRecebidas'))
    
    titulo_resposta = f"Re: {mensagemOriginal.titulo}"
    
    return render_template('mensagem.html', nome=destinatario.nome,titulo=titulo_resposta, texto=f"\n\n---------- Mensagem Original ----------\n{mensagemOriginal.texto}")


@app.context_processor
def utility_processor():
    return dict(contarMensagensNaoLidas=contarMensagensNaoLidas)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.context_processor
def inject_now():
    return {'now': datetime.datetime.now()}


if __name__ == "__main__":
    init_db()    
    app.run(debug=True)


