from src.models.user import db
from datetime import datetime
import json

class MapaMental(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    disciplina_id = db.Column(db.Integer, db.ForeignKey('disciplina.id'), nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    nodos = db.Column(db.Text, nullable=False)  # JSON string
    arestas = db.Column(db.Text, nullable=False)  # JSON string
    thumbnail_url = db.Column(db.String(500))
    preco = db.Column(db.Float, default=0.0)
    autor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)

    # Relacionamento com autor
    autor = db.relationship('User', backref='mapas_criados')

    def __repr__(self):
        return f'<MapaMental {self.titulo}>'

    def get_nodos(self):
        """Retorna os nodos como objeto Python"""
        try:
            return json.loads(self.nodos) if self.nodos else []
        except json.JSONDecodeError:
            return []

    def set_nodos(self, nodos_list):
        """Define os nodos a partir de uma lista Python"""
        self.nodos = json.dumps(nodos_list)

    def get_arestas(self):
        """Retorna as arestas como objeto Python"""
        try:
            return json.loads(self.arestas) if self.arestas else []
        except json.JSONDecodeError:
            return []

    def set_arestas(self, arestas_list):
        """Define as arestas a partir de uma lista Python"""
        self.arestas = json.dumps(arestas_list)

    def to_dict(self):
        return {
            'id': self.id,
            'disciplina_id': self.disciplina_id,
            'titulo': self.titulo,
            'nodos': self.get_nodos(),
            'arestas': self.get_arestas(),
            'thumbnail_url': self.thumbnail_url,
            'preco': self.preco,
            'autor_id': self.autor_id,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None,
            'ativo': self.ativo,
            'disciplina_nome': self.disciplina.nome if self.disciplina else None
        }

