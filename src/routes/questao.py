from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.questao import Questao
from src.models.disciplina import Disciplina
import random

questao_bp = Blueprint('questao', __name__)

@questao_bp.route('/questoes', methods=['GET'])
def listar_questoes():
    """Lista questões com filtros opcionais"""
    try:
        disciplina_id = request.args.get('disciplina_id', type=int)
        dificuldade = request.args.get('dificuldade')
        limite = request.args.get('limite', type=int, default=20)
        incluir_resposta = request.args.get('incluir_resposta', type=bool, default=False)
        
        query = Questao.query.filter_by(ativo=True)
        
        if disciplina_id:
            query = query.filter_by(disciplina_id=disciplina_id)
        if dificuldade:
            query = query.filter_by(dificuldade=dificuldade)
        
        questoes = query.limit(limite).all()
        
        # Embaralhar questões para variedade
        random.shuffle(questoes)
        
        return jsonify([questao.to_dict(include_resposta=incluir_resposta) for questao in questoes]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@questao_bp.route('/questoes', methods=['POST'])
def criar_questao():
    """Cria uma nova questão"""
    try:
        data = request.get_json()
        
        required_fields = ['texto_questao', 'disciplina_id', 'alternativas', 'resposta_correta', 'autor_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        # Verificar se a disciplina existe
        disciplina = Disciplina.query.get(data['disciplina_id'])
        if not disciplina:
            return jsonify({'error': 'Disciplina não encontrada'}), 404
        
        # Validar alternativas
        alternativas = data['alternativas']
        if not isinstance(alternativas, list) or len(alternativas) < 2:
            return jsonify({'error': 'Deve haver pelo menos 2 alternativas'}), 400
        
        # Validar resposta correta
        resposta_correta = data['resposta_correta']
        if not isinstance(resposta_correta, int) or resposta_correta < 0 or resposta_correta >= len(alternativas):
            return jsonify({'error': 'Índice da resposta correta inválido'}), 400
        
        questao = Questao(
            texto_questao=data['texto_questao'],
            disciplina_id=data['disciplina_id'],
            resposta_correta=resposta_correta,
            explicacao=data.get('explicacao', ''),
            dificuldade=data.get('dificuldade', 'medio'),
            autor_id=data['autor_id']
        )
        
        questao.set_alternativas(alternativas)
        
        db.session.add(questao)
        db.session.commit()
        
        return jsonify(questao.to_dict(include_resposta=True)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@questao_bp.route('/questoes/<int:questao_id>', methods=['GET'])
def obter_questao(questao_id):
    """Obtém uma questão específica"""
    try:
        incluir_resposta = request.args.get('incluir_resposta', type=bool, default=False)
        questao = Questao.query.filter_by(id=questao_id, ativo=True).first_or_404()
        return jsonify(questao.to_dict(include_resposta=incluir_resposta)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@questao_bp.route('/questoes/<int:questao_id>', methods=['PUT'])
def atualizar_questao(questao_id):
    """Atualiza uma questão"""
    try:
        questao = Questao.query.filter_by(id=questao_id, ativo=True).first_or_404()
        data = request.get_json()
        
        if 'texto_questao' in data:
            questao.texto_questao = data['texto_questao']
        if 'alternativas' in data:
            alternativas = data['alternativas']
            if not isinstance(alternativas, list) or len(alternativas) < 2:
                return jsonify({'error': 'Deve haver pelo menos 2 alternativas'}), 400
            questao.set_alternativas(alternativas)
        if 'resposta_correta' in data:
            resposta_correta = data['resposta_correta']
            alternativas_atuais = questao.get_alternativas()
            if not isinstance(resposta_correta, int) or resposta_correta < 0 or resposta_correta >= len(alternativas_atuais):
                return jsonify({'error': 'Índice da resposta correta inválido'}), 400
            questao.resposta_correta = resposta_correta
        if 'explicacao' in data:
            questao.explicacao = data['explicacao']
        if 'dificuldade' in data:
            questao.dificuldade = data['dificuldade']
        
        db.session.commit()
        return jsonify(questao.to_dict(include_resposta=True)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@questao_bp.route('/questoes/<int:questao_id>', methods=['DELETE'])
def deletar_questao(questao_id):
    """Deleta (desativa) uma questão"""
    try:
        questao = Questao.query.filter_by(id=questao_id, ativo=True).first_or_404()
        questao.ativo = False
        db.session.commit()
        return jsonify({'message': 'Questão deletada com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@questao_bp.route('/disciplinas/<int:disciplina_id>/questoes', methods=['GET'])
def listar_questoes_por_disciplina(disciplina_id):
    """Lista questões de uma disciplina específica"""
    try:
        disciplina = Disciplina.query.get_or_404(disciplina_id)
        limite = request.args.get('limite', type=int, default=20)
        dificuldade = request.args.get('dificuldade')
        incluir_resposta = request.args.get('incluir_resposta', type=bool, default=False)
        
        query = Questao.query.filter_by(disciplina_id=disciplina_id, ativo=True)
        
        if dificuldade:
            query = query.filter_by(dificuldade=dificuldade)
        
        questoes = query.limit(limite).all()
        
        # Embaralhar questões
        random.shuffle(questoes)
        
        return jsonify([questao.to_dict(include_resposta=incluir_resposta) for questao in questoes]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

