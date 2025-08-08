from src.models.user import db
from datetime import datetime

class RespostaQuestao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sessao_id = db.Column(db.Integer, db.ForeignKey('sessao_treinamento.id'), nullable=False)
    questao_id = db.Column(db.Integer, db.ForeignKey('questao.id'), nullable=False)
    resposta_usuario = db.Column(db.Integer, nullable=False)  # Índice da resposta escolhida
    correta = db.Column(db.Boolean, nullable=False)
    tempo_resposta_segundos = db.Column(db.Integer, default=0)
    data_resposta = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<RespostaQuestao {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'sessao_id': self.sessao_id,
            'questao_id': self.questao_id,
            'resposta_usuario': self.resposta_usuario,
            'correta': self.correta,
            'tempo_resposta_segundos': self.tempo_resposta_segundos,
            'data_resposta': self.data_resposta.isoformat() if self.data_resposta else None
        }

