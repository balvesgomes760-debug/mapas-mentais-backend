from flask import Blueprint, request, jsonify
from src.models.user import db, User
from src.models.metrica_usuario import MetricaUsuario
from src.models.disciplina import Disciplina
from src.models.sessao_treinamento import SessaoTreinamento
from sqlalchemy import func
from datetime import datetime, timedelta

metrica_bp = Blueprint('metrica', __name__)

@metrica_bp.route('/metricas/usuario/<int:usuario_id>', methods=['GET'])
def obter_metricas_usuario(usuario_id):
    """Obtém métricas gerais de um usuário"""
    try:
        usuario = User.query.get_or_404(usuario_id)
        
        # Métricas por disciplina
        metricas = MetricaUsuario.query.filter_by(usuario_id=usuario_id).all()
        
        # Estatísticas gerais
        total_tempo_minutos = sum(m.tempo_estudo_minutos for m in metricas)
        taxa_acertos_media = sum(m.taxa_acertos for m in metricas) / len(metricas) if metricas else 0
        maior_constancia = max(m.dias_constancia for m in metricas) if metricas else 0
        
        # Sessões recentes
        sessoes_recentes = SessaoTreinamento.query.filter_by(
            usuario_id=usuario_id,
            finalizada=True
        ).order_by(SessaoTreinamento.data_fim.desc()).limit(10).all()
        
        resultado = {
            'usuario': usuario.to_dict(),
            'estatisticas_gerais': {
                'total_tempo_minutos': total_tempo_minutos,
                'total_tempo_horas': round(total_tempo_minutos / 60, 1),
                'taxa_acertos_media': round(taxa_acertos_media, 2),
                'maior_constancia': maior_constancia,
                'disciplinas_estudadas': len(metricas)
            },
            'metricas_por_disciplina': [m.to_dict() for m in metricas],
            'sessoes_recentes': [s.to_dict() for s in sessoes_recentes]
        }
        
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@metrica_bp.route('/metricas/usuario/<int:usuario_id>/disciplina/<int:disciplina_id>', methods=['GET'])
def obter_metricas_disciplina(usuario_id, disciplina_id):
    """Obtém métricas específicas de uma disciplina"""
    try:
        usuario = User.query.get_or_404(usuario_id)
        disciplina = Disciplina.query.get_or_404(disciplina_id)
        
        metrica = MetricaUsuario.query.filter_by(
            usuario_id=usuario_id,
            disciplina_id=disciplina_id
        ).first()
        
        if not metrica:
            # Criar métrica inicial se não existir
            metrica = MetricaUsuario(
                usuario_id=usuario_id,
                disciplina_id=disciplina_id
            )
            db.session.add(metrica)
            db.session.commit()
        
        # Sessões da disciplina
        sessoes = SessaoTreinamento.query.filter_by(
            usuario_id=usuario_id,
            disciplina_id=disciplina_id,
            finalizada=True
        ).order_by(SessaoTreinamento.data_fim.desc()).all()
        
        resultado = {
            'metrica': metrica.to_dict(),
            'disciplina': disciplina.to_dict(),
            'sessoes': [s.to_dict() for s in sessoes],
            'total_sessoes': len(sessoes)
        }
        
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@metrica_bp.route('/metricas/dashboard/<int:usuario_id>', methods=['GET'])
def obter_dashboard_metricas(usuario_id):
    """Obtém dados para o dashboard de métricas"""
    try:
        usuario = User.query.get_or_404(usuario_id)
        
        # Métricas por disciplina
        metricas = MetricaUsuario.query.filter_by(usuario_id=usuario_id).all()
        
        # Dados para gráficos
        # 1. Tempo de estudo por disciplina (últimos 7 dias)
        data_limite = datetime.now() - timedelta(days=7)
        sessoes_semana = SessaoTreinamento.query.filter(
            SessaoTreinamento.usuario_id == usuario_id,
            SessaoTreinamento.finalizada == True,
            SessaoTreinamento.data_fim >= data_limite
        ).all()
        
        # Agrupar por dia
        tempo_por_dia = {}
        for sessao in sessoes_semana:
            if sessao.data_fim:
                dia = sessao.data_fim.strftime('%Y-%m-%d')
                minutos = sessao.tempo_total_segundos // 60
                tempo_por_dia[dia] = tempo_por_dia.get(dia, 0) + minutos
        
        # 2. Taxa de acertos por disciplina
        acertos_por_disciplina = []
        for metrica in metricas:
            acertos_por_disciplina.append({
                'disciplina': metrica.disciplina.nome,
                'taxa_acertos': metrica.taxa_acertos,
                'cor': metrica.disciplina.cor
            })
        
        # 3. Evolução da constância (últimos 14 dias)
        constancia_dados = []
        for i in range(14):
            data = datetime.now() - timedelta(days=13-i)
            # Verificar se houve atividade neste dia
            atividade = SessaoTreinamento.query.filter(
                SessaoTreinamento.usuario_id == usuario_id,
                SessaoTreinamento.finalizada == True,
                func.date(SessaoTreinamento.data_fim) == data.date()
            ).first()
            
            constancia_dados.append({
                'data': data.strftime('%Y-%m-%d'),
                'estudou': bool(atividade)
            })
        
        # Estatísticas resumidas
        total_tempo = sum(m.tempo_estudo_minutos for m in metricas)
        taxa_media = sum(m.taxa_acertos for m in metricas) / len(metricas) if metricas else 0
        maior_streak = max(m.dias_constancia for m in metricas) if metricas else 0
        
        resultado = {
            'resumo': {
                'tempo_total_horas': round(total_tempo / 60, 1),
                'taxa_acertos_media': round(taxa_media, 1),
                'streak_atual': maior_streak
            },
            'tempo_por_dia': tempo_por_dia,
            'acertos_por_disciplina': acertos_por_disciplina,
            'constancia_14_dias': constancia_dados,
            'metricas_disciplinas': [m.to_dict() for m in metricas]
        }
        
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@metrica_bp.route('/metricas/insights/<int:usuario_id>', methods=['GET'])
def gerar_insights(usuario_id):
    """Gera insights automáticos para o usuário"""
    try:
        usuario = User.query.get_or_404(usuario_id)
        metricas = MetricaUsuario.query.filter_by(usuario_id=usuario_id).all()
        
        insights = []
        
        for metrica in metricas:
            disciplina_nome = metrica.disciplina.nome
            
            # Insight sobre taxa de acertos baixa
            if metrica.taxa_acertos < 60:
                insights.append({
                    'tipo': 'alerta',
                    'titulo': f'Taxa de acertos baixa em {disciplina_nome}',
                    'descricao': f'Sua taxa de acertos em {disciplina_nome} está em {metrica.taxa_acertos:.1f}%. Considere revisar o conteúdo.',
                    'acao': 'Revisar mapas mentais',
                    'prioridade': 'alta'
                })
            
            # Insight sobre constância
            if metrica.dias_constancia >= 7:
                insights.append({
                    'tipo': 'parabens',
                    'titulo': f'Excelente constância em {disciplina_nome}!',
                    'descricao': f'Você está há {metrica.dias_constancia} dias estudando {disciplina_nome} consistentemente.',
                    'acao': 'Continue assim!',
                    'prioridade': 'baixa'
                })
            elif metrica.dias_constancia == 0:
                insights.append({
                    'tipo': 'motivacao',
                    'titulo': f'Que tal estudar {disciplina_nome} hoje?',
                    'descricao': f'Você não estuda {disciplina_nome} há alguns dias. Uma sessão rápida pode ajudar!',
                    'acao': 'Iniciar treinamento',
                    'prioridade': 'media'
                })
            
            # Insight sobre tempo de estudo
            if metrica.tempo_estudo_minutos < 60:  # Menos de 1 hora total
                insights.append({
                    'tipo': 'sugestao',
                    'titulo': f'Aumente o tempo de estudo em {disciplina_nome}',
                    'descricao': f'Você estudou apenas {metrica.tempo_estudo_minutos} minutos de {disciplina_nome}. Que tal dedicar mais tempo?',
                    'acao': 'Criar plano de estudos',
                    'prioridade': 'media'
                })
        
        # Ordenar por prioridade
        ordem_prioridade = {'alta': 0, 'media': 1, 'baixa': 2}
        insights.sort(key=lambda x: ordem_prioridade.get(x['prioridade'], 3))
        
        return jsonify(insights[:5]), 200  # Retornar apenas os 5 principais
    except Exception as e:
        return jsonify({'error': str(e)}), 500

