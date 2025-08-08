from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models.mapa_mental import MapaMental
from src.models.disciplina import Disciplina

mapa_mental_bp = Blueprint('mapa_mental', __name__)

@mapa_mental_bp.route('/mapas', methods=['GET'])
def listar_mapas():
    """Lista todos os mapas mentais"""
    try:
        disciplina_id = request.args.get('disciplina_id', type=int)
        autor_id = request.args.get('autor_id', type=int)
        
        query = MapaMental.query.filter_by(ativo=True)
        
        if disciplina_id:
            query = query.filter_by(disciplina_id=disciplina_id)
        if autor_id:
            query = query.filter_by(autor_id=autor_id)
        
        mapas = query.all()
        return jsonify([mapa.to_dict() for mapa in mapas]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mapa_mental_bp.route('/mapas', methods=['POST'])
def criar_mapa():
    """Cria um novo mapa mental"""
    try:
        data = request.get_json()
        
        required_fields = ['titulo', 'disciplina_id', 'autor_id', 'nodos', 'arestas']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        # Verificar se a disciplina existe
        disciplina = Disciplina.query.get(data['disciplina_id'])
        if not disciplina:
            return jsonify({'error': 'Disciplina não encontrada'}), 404
        
        mapa = MapaMental(
            titulo=data['titulo'],
            disciplina_id=data['disciplina_id'],
            autor_id=data['autor_id'],
            preco=data.get('preco', 0.0)
        )
        
        # Definir nodos e arestas
        mapa.set_nodos(data['nodos'])
        mapa.set_arestas(data['arestas'])
        
        if 'thumbnail_url' in data:
            mapa.thumbnail_url = data['thumbnail_url']
        
        db.session.add(mapa)
        db.session.commit()
        
        return jsonify(mapa.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@mapa_mental_bp.route('/mapas/<int:mapa_id>', methods=['GET'])
def obter_mapa(mapa_id):
    """Obtém um mapa mental específico"""
    try:
        mapa = MapaMental.query.filter_by(id=mapa_id, ativo=True).first_or_404()
        return jsonify(mapa.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mapa_mental_bp.route('/mapas/<int:mapa_id>', methods=['PUT'])
def atualizar_mapa(mapa_id):
    """Atualiza um mapa mental"""
    try:
        mapa = MapaMental.query.filter_by(id=mapa_id, ativo=True).first_or_404()
        data = request.get_json()
        
        if 'titulo' in data:
            mapa.titulo = data['titulo']
        if 'preco' in data:
            mapa.preco = data['preco']
        if 'nodos' in data:
            mapa.set_nodos(data['nodos'])
        if 'arestas' in data:
            mapa.set_arestas(data['arestas'])
        if 'thumbnail_url' in data:
            mapa.thumbnail_url = data['thumbnail_url']
        
        db.session.commit()
        return jsonify(mapa.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@mapa_mental_bp.route('/mapas/<int:mapa_id>', methods=['DELETE'])
def deletar_mapa(mapa_id):
    """Deleta (desativa) um mapa mental"""
    try:
        mapa = MapaMental.query.filter_by(id=mapa_id, ativo=True).first_or_404()
        mapa.ativo = False
        db.session.commit()
        return jsonify({'message': 'Mapa mental deletado com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@mapa_mental_bp.route('/disciplinas/<int:disciplina_id>/mapas', methods=['GET'])
def listar_mapas_por_disciplina(disciplina_id):
    """Lista mapas mentais de uma disciplina específica"""
    try:
        disciplina = Disciplina.query.get_or_404(disciplina_id)
        mapas = MapaMental.query.filter_by(disciplina_id=disciplina_id, ativo=True).all()
        return jsonify([mapa.to_dict() for mapa in mapas]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

