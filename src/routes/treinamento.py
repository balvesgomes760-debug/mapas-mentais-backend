from flask import Blueprint, request, jsonify
from src.models.user import db, User
from src.models.sessao_treinamento import SessaoTreinamento
from src.models.resposta_questao import RespostaQuestao
from src.models.questao import Questao
from src.models.metrica_usuario import MetricaUsuario
from datetime import datetime

treinamento_bp = Blueprint('treinamento', __name__)

@treinamento_bp.route('/treinamento/iniciar', methods=['POST'])
def iniciar_sessao():
    """Inicia uma nova sessão de treinamento"""
    try:
        data = request.get_json()
        
        required_fields = ['usuario_id', 'tipo']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        # Verificar se o usuário existe
        usuario = User.query.get(data['usuario_id'])
        if not usuario:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Verificar se há sessão ativa
        sessao_ativa = SessaoTreinamento.query.filter_by(
            usuario_id=data['usuario_id'],
            finalizada=False
        ).first()
        
        if sessao_ativa:
            return jsonify({'error': 'Já existe uma sessão ativa', 'sessao': sessao_ativa.to_dict()}), 400
        
        sessao = SessaoTreinamento(
            usuario_id=data['usuario_id'],
            tipo=data['tipo'],
            disciplina_id=data.get('disciplina_id'),
            total_itens=data.get('total_itens', 10)
        )
        
        db.session.add(sessao)
        db.session.commit()
        
        return jsonify(sessao.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@treinamento_bp.route('/treinamento/sessoes/<int:sessao_id>', methods=['GET'])
def obter_sessao(sessao_id):
    """Obtém informações de uma sessão"""
    try:
        sessao = SessaoTreinamento.query.get_or_404(sessao_id)
        return jsonify(sessao.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@treinamento_bp.route('/treinamento/responder', methods=['POST'])
def responder_questao():
    """Registra a resposta de uma questão"""
    try:
        data = request.get_json()
        
        required_fields = ['sessao_id', 'questao_id', 'resposta_usuario']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        # Verificar se a sessão existe e está ativa
        sessao = SessaoTreinamento.query.filter_by(
            id=data['sessao_id'],
            finalizada=False
        ).first()
        
        if not sessao:
            return jsonify({'error': 'Sessão não encontrada ou já finalizada'}), 404
        
        # Verificar se a questão existe
        questao = Questao.query.get(data['questao_id'])
        if not questao:
            return jsonify({'error': 'Questão não encontrada'}), 404
        
        # Verificar se já foi respondida
        resposta_existente = RespostaQuestao.query.filter_by(
            sessao_id=data['sessao_id'],
            questao_id=data['questao_id']
        ).first()
        
        if resposta_existente:
            return jsonify({'error': 'Questão já foi respondida nesta sessão'}), 400
        
        # Verificar se a resposta está correta
        correta = data['resposta_usuario'] == questao.resposta_correta
        
        resposta = RespostaQuestao(
            sessao_id=data['sessao_id'],
            questao_id=data['questao_id'],
            resposta_usuario=data['resposta_usuario'],
            correta=correta,
            tempo_resposta_segundos=data.get('tempo_resposta_segundos', 0)
        )
        
        db.session.add(resposta)
        
        # Atualizar progresso da sessão
        sessao.itens_completados += 1
        
        db.session.commit()
        
        # Retornar feedback
        feedback = {
            'correta': correta,
            'resposta_correta': questao.resposta_correta,
            'explicacao': questao.explicacao,
            'progresso': {
                'completados': sessao.itens_completados,
                'total': sessao.total_itens
            }
        }
        
        return jsonify(feedback), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@treinamento_bp.route('/treinamento/finalizar/<int:sessao_id>', methods=['POST'])
def finalizar_sessao(sessao_id):
    """Finaliza uma sessão de treinamento"""
    try:
        sessao = SessaoTreinamento.query.filter_by(
            id=sessao_id,
            finalizada=False
        ).first()
        
        if not sessao:
            return jsonify({'error': 'Sessão não encontrada ou já finalizada'}), 404
        
        # Finalizar sessão
        sessao.finalizar_sessao()
        
        # Calcular métricas
        taxa_acertos = sessao.calcular_taxa_acertos()
        tempo_minutos = sessao.tempo_total_segundos // 60
        
        # Atualizar métricas do usuário
        if sessao.disciplina_id:
            metrica = MetricaUsuario.query.filter_by(
                usuario_id=sessao.usuario_id,
                disciplina_id=sessao.disciplina_id
            ).first()
            
            if not metrica:
                metrica = MetricaUsuario(
                    usuario_id=sessao.usuario_id,
                    disciplina_id=sessao.disciplina_id
                )
                db.session.add(metrica)
            
            metrica.adicionar_tempo_estudo(tempo_minutos)
            metrica.atualizar_taxa_acertos(taxa_acertos)
        
        db.session.commit()
        
        resultado = {
            'sessao': sessao.to_dict(),
            'taxa_acertos': taxa_acertos,
            'tempo_total_minutos': tempo_minutos,
            'respostas_corretas': sum(1 for r in sessao.respostas if r.correta),
            'total_questoes': len(sessao.respostas)
        }
        
        return jsonify(resultado), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@treinamento_bp.route('/treinamento/usuario/<int:usuario_id>/sessoes', methods=['GET'])
def listar_sessoes_usuario(usuario_id):
    """Lista sessões de treinamento de um usuário"""
    try:
        usuario = User.query.get_or_404(usuario_id)
        
        sessoes = SessaoTreinamento.query.filter_by(usuario_id=usuario_id).order_by(
            SessaoTreinamento.data_inicio.desc()
        ).all()
        
        return jsonify([sessao.to_dict() for sessao in sessoes]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

