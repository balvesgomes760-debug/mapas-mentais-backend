from src.models.user import db
from datetime import datetime

class Disciplina(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cor = db.Column(db.String(7), default='#0EA5A4')  # Hex color
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    mapas = db.relationship('MapaMental', backref='disciplina', lazy=True, cascade='all, delete-orphan')
    resumos = db.relationship('Resumo', backref='disciplina', lazy=True, cascade='all, delete-orphan')
    questoes = db.relationship('Questao', backref='disciplina', lazy=True, cascade='all, delete-orphan')
    metricas = db.relationship('MetricaUsuario', backref='disciplina', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Disciplina {self.nome}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'cor': self.cor,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'mapas_count': len(self.mapas),
            'resumos_count': len(self.resumos),
            'questoes_count': len(self.questoes)
        }

