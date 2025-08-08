from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    creditos = db.Column(db.Float, default=0.0)
    tipo_usuario = db.Column(db.String(20), default='estudante')  # estudante, professor, admin
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        """Define a senha do usuário (hash)"""
        self.senha_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica se a senha está correta"""
        return check_password_hash(self.senha_hash, password)

    def debitar_creditos(self, valor):
        """Debita créditos da conta do usuário"""
        if self.creditos >= valor:
            self.creditos -= valor
            return True
        return False

    def creditar_creditos(self, valor):
        """Adiciona créditos à conta do usuário"""
        self.creditos += valor

    def tem_creditos_suficientes(self, valor):
        """Verifica se o usuário tem créditos suficientes"""
        return self.creditos >= valor

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'creditos': self.creditos,
            'tipo_usuario': self.tipo_usuario,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None,
            'ativo': self.ativo
        }
