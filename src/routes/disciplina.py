from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.disciplina import Disciplina

disciplina_bp = Blueprint('disciplina', __name__)

@disciplina_bp.route('/disciplinas', methods=['GET'])
def listar_disciplinas():
    """Lista todas as disciplinas"""
    try:
        disciplinas = Disciplina.query.all()
        return jsonify([disciplina.to_dict() for disciplina in disciplinas]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@disciplina_bp.route('/disciplinas', methods=['POST'])
def criar_disciplina():
    """Cria uma nova disciplina"""
    try:
        data = request.get_json()
        
        if not data or 'nome' not in data:
            return jsonify({'error': 'Nome da disciplina é obrigatório'}), 400
        
        # Verificar se já existe disciplina com esse nome
        disciplina_existente = Disciplina.query.filter_by(nome=data['nome']).first()
        if disciplina_existente:
            return jsonify({'error': 'Já existe uma disciplina com esse nome'}), 400
        
        disciplina = Disciplina(
            nome=data['nome'],
            cor=data.get('cor', '#0EA5A4')
        )
        
        db.session.add(disciplina)
        db.session.commit()
        
        return jsonify(disciplina.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@disciplina_bp.route('/disciplinas/<int:disciplina_id>', methods=['GET'])
def obter_disciplina(disciplina_id):
    """Obtém uma disciplina específica"""
    try:
        disciplina = Disciplina.query.get_or_404(disciplina_id)
        return jsonify(disciplina.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@disciplina_bp.route('/disciplinas/<int:disciplina_id>', methods=['PUT'])
def atualizar_disciplina(disciplina_id):
    """Atualiza uma disciplina"""
    try:
        disciplina = Disciplina.query.get_or_404(disciplina_id)
        data = request.get_json()
        
        if 'nome' in data:
            # Verificar se já existe outra disciplina com esse nome
            disciplina_existente = Disciplina.query.filter(
                Disciplina.nome == data['nome'],
                Disciplina.id != disciplina_id
            ).first()
            if disciplina_existente:
                return jsonify({'error': 'Já existe uma disciplina com esse nome'}), 400
            disciplina.nome = data['nome']
        
        if 'cor' in data:
            disciplina.cor = data['cor']
        
        db.session.commit()
        return jsonify(disciplina.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@disciplina_bp.route('/disciplinas/<int:disciplina_id>', methods=['DELETE'])
def deletar_disciplina(disciplina_id):
    """Deleta uma disciplina"""
    try:
        disciplina = Disciplina.query.get_or_404(disciplina_id)
        db.session.delete(disciplina)
        db.session.commit()
        return jsonify({'message': 'Disciplina deletada com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

