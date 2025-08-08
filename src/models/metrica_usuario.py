from src.models.user import db
from datetime import datetime, date

class MetricaUsuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    disciplina_id = db.Column(db.Integer, db.ForeignKey('disciplina.id'), nullable=False)
    tempo_estudo_minutos = db.Column(db.Integer, default=0)
    taxa_acertos = db.Column(db.Float, default=0.0)  # Percentual 0-100
    dias_constancia = db.Column(db.Integer, default=0)
    ultima_atividade = db.Column(db.Date, default=date.today)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    usuario = db.relationship('User', backref='metricas')

    def __repr__(self):
        return f'<MetricaUsuario {self.usuario_id}-{self.disciplina_id}>'

    def atualizar_constancia(self):
        """Atualiza a constância baseada na última atividade"""
        hoje = date.today()
        if self.ultima_atividade:
            dias_diferenca = (hoje - self.ultima_atividade).days
            if dias_diferenca == 1:
                # Estudou ontem, incrementa constância
                self.dias_constancia += 1
            elif dias_diferenca > 1:
                # Quebrou a sequência
                self.dias_constancia = 1
            # Se dias_diferenca == 0, já estudou hoje, mantém constância
        else:
            # Primeira atividade
            self.dias_constancia = 1
        
        self.ultima_atividade = hoje

    def adicionar_tempo_estudo(self, minutos):
        """Adiciona tempo de estudo e atualiza constância"""
        self.tempo_estudo_minutos += minutos
        self.atualizar_constancia()

    def atualizar_taxa_acertos(self, nova_taxa):
        """Atualiza a taxa de acertos (média ponderada)"""
        if self.taxa_acertos == 0:
            self.taxa_acertos = nova_taxa
        else:
            # Média ponderada: 70% da taxa atual + 30% da nova taxa
            self.taxa_acertos = (self.taxa_acertos * 0.7) + (nova_taxa * 0.3)

    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'disciplina_id': self.disciplina_id,
            'tempo_estudo_minutos': self.tempo_estudo_minutos,
            'taxa_acertos': round(self.taxa_acertos, 2),
            'dias_constancia': self.dias_constancia,
            'ultima_atividade': self.ultima_atividade.isoformat() if self.ultima_atividade else None,
            'data_atualizacao': self.data_atualizacao.isoformat() if self.data_atualizacao else None,
            'disciplina_nome': self.disciplina.nome if self.disciplina else None
        }

