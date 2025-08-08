from src.models.user import db
from datetime import datetime

class Resumo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    disciplina_id = db.Column(db.Integer, db.ForeignKey('disciplina.id'), nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    conteudo = db.Column(db.Text, nullable=False)  # Markdown/HTML
    preco = db.Column(db.Float, default=0.0)
    autor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)

    # Relacionamento com autor
    autor = db.relationship('User', backref='resumos_criados')

    def __repr__(self):
        return f'<Resumo {self.titulo}>'

    def to_dict(self):
        return {
            'id': self.id,
            'disciplina_id': self.disciplina_id,
            'titulo': self.titulo,
            'conteudo': self.conteudo,
            'preco': self.preco,
            'autor_id': self.autor_id,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None,
            'ativo': self.ativo,
            'disciplina_nome': self.disciplina.nome if self.disciplina else None
        }

