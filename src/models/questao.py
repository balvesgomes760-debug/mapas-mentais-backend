from src.models.user import db
from datetime import datetime
import json

class Questao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    disciplina_id = db.Column(db.Integer, db.ForeignKey('disciplina.id'), nullable=False)
    texto_questao = db.Column(db.Text, nullable=False)
    alternativas = db.Column(db.Text, nullable=False)  # JSON string
    resposta_correta = db.Column(db.Integer, nullable=False)  # Índice da resposta correta (0-3)
    explicacao = db.Column(db.Text)
    dificuldade = db.Column(db.String(20), default='medio')  # facil, medio, dificil
    autor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)

    # Relacionamento com autor
    autor = db.relationship('User', backref='questoes_criadas')
    
    # Relacionamento com respostas
    respostas = db.relationship('RespostaQuestao', backref='questao', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Questao {self.id}>'

    def get_alternativas(self):
        """Retorna as alternativas como lista Python"""
        try:
            return json.loads(self.alternativas) if self.alternativas else []
        except json.JSONDecodeError:
            return []

    def set_alternativas(self, alternativas_list):
        """Define as alternativas a partir de uma lista Python"""
        self.alternativas = json.dumps(alternativas_list)

    def to_dict(self, include_resposta=False):
        data = {
            'id': self.id,
            'disciplina_id': self.disciplina_id,
            'texto_questao': self.texto_questao,
            'alternativas': self.get_alternativas(),
            'explicacao': self.explicacao,
            'dificuldade': self.dificuldade,
            'autor_id': self.autor_id,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'ativo': self.ativo,
            'disciplina_nome': self.disciplina.nome if self.disciplina else None
        }
        
        # Incluir resposta correta apenas se solicitado (para administradores)
        if include_resposta:
            data['resposta_correta'] = self.resposta_correta
            
        return data

