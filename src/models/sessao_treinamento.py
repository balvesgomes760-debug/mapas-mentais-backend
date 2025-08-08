from src.models.user import db
from datetime import datetime

class SessaoTreinamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # questoes, flashcards, mapas
    disciplina_id = db.Column(db.Integer, db.ForeignKey('disciplina.id'))
    total_itens = db.Column(db.Integer, default=0)
    itens_completados = db.Column(db.Integer, default=0)
    tempo_total_segundos = db.Column(db.Integer, default=0)
    data_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    data_fim = db.Column(db.DateTime)
    finalizada = db.Column(db.Boolean, default=False)

    # Relacionamentos
    usuario = db.relationship('User', backref='sessoes_treinamento')
    respostas = db.relationship('RespostaQuestao', backref='sessao', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<SessaoTreinamento {self.id} - {self.tipo}>'

    def calcular_taxa_acertos(self):
        """Calcula a taxa de acertos da sessão"""
        if not self.respostas:
            return 0.0
        
        acertos = sum(1 for resposta in self.respostas if resposta.correta)
        return (acertos / len(self.respostas)) * 100

    def finalizar_sessao(self):
        """Finaliza a sessão e atualiza os dados"""
        self.data_fim = datetime.utcnow()
        self.finalizada = True
        if self.data_inicio:
            delta = self.data_fim - self.data_inicio
            self.tempo_total_segundos = int(delta.total_seconds())

    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'tipo': self.tipo,
            'disciplina_id': self.disciplina_id,
            'total_itens': self.total_itens,
            'itens_completados': self.itens_completados,
            'tempo_total_segundos': self.tempo_total_segundos,
            'data_inicio': self.data_inicio.isoformat() if self.data_inicio else None,
            'data_fim': self.data_fim.isoformat() if self.data_fim else None,
            'finalizada': self.finalizada,
            'taxa_acertos': self.calcular_taxa_acertos(),
            'disciplina_nome': self.disciplina.nome if self.disciplina else None
        }

