"""
Script para popular o banco de dados com dados de exemplo
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.models.user import db, User
from src.models.disciplina import Disciplina
from src.models.mapa_mental import MapaMental
from src.models.questao import Questao
from src.models.metrica_usuario import MetricaUsuario

def criar_dados_exemplo():
    """Cria dados de exemplo para testar a aplicação"""
    
    # Criar usuário de exemplo
    usuario = User(
        username='professor_joao',
        email='joao@exemplo.com',
        creditos=100.0,
        tipo_usuario='professor'
    )
    usuario.set_password('123456')
    db.session.add(usuario)
    
    # Criar disciplinas
    disciplinas_data = [
        {'nome': 'Nutrição', 'cor': '#0EA5A4'},
        {'nome': 'Direito Tributário', 'cor': '#06B6D4'},
        {'nome': 'Física', 'cor': '#8B5CF6'},
        {'nome': 'Matemática', 'cor': '#F59E0B'}
    ]
    
    disciplinas = []
    for disc_data in disciplinas_data:
        disciplina = Disciplina(**disc_data)
        db.session.add(disciplina)
        disciplinas.append(disciplina)
    
    db.session.commit()  # Commit para obter IDs
    
    # Criar mapas mentais de exemplo
    mapas_data = [
        {
            'titulo': 'Macronutrientes Essenciais',
            'disciplina_id': disciplinas[0].id,
            'autor_id': usuario.id,
            'nodos': [
                {'id': '1', 'text': 'Macronutrientes', 'x': 200, 'y': 100, 'color': '#0EA5A4'},
                {'id': '2', 'text': 'Carboidratos', 'x': 100, 'y': 200, 'color': '#06B6D4'},
                {'id': '3', 'text': 'Proteínas', 'x': 200, 'y': 200, 'color': '#06B6D4'},
                {'id': '4', 'text': 'Lipídios', 'x': 300, 'y': 200, 'color': '#06B6D4'}
            ],
            'arestas': [
                {'from': '1', 'to': '2'},
                {'from': '1', 'to': '3'},
                {'from': '1', 'to': '4'}
            ],
            'preco': 5.0
        },
        {
            'titulo': 'Tributos Federais',
            'disciplina_id': disciplinas[1].id,
            'autor_id': usuario.id,
            'nodos': [
                {'id': '1', 'text': 'Tributos Federais', 'x': 200, 'y': 100, 'color': '#06B6D4'},
                {'id': '2', 'text': 'Imposto de Renda', 'x': 100, 'y': 200, 'color': '#0EA5A4'},
                {'id': '3', 'text': 'IPI', 'x': 200, 'y': 200, 'color': '#0EA5A4'},
                {'id': '4', 'text': 'IOF', 'x': 300, 'y': 200, 'color': '#0EA5A4'}
            ],
            'arestas': [
                {'from': '1', 'to': '2'},
                {'from': '1', 'to': '3'},
                {'from': '1', 'to': '4'}
            ],
            'preco': 8.0
        }
    ]
    
    for mapa_data in mapas_data:
        mapa = MapaMental(
            titulo=mapa_data['titulo'],
            disciplina_id=mapa_data['disciplina_id'],
            autor_id=mapa_data['autor_id'],
            preco=mapa_data['preco']
        )
        mapa.set_nodos(mapa_data['nodos'])
        mapa.set_arestas(mapa_data['arestas'])
        db.session.add(mapa)
    
    # Criar questões de exemplo
    questoes_data = [
        {
            'texto_questao': 'Qual é o principal objetivo da nutrição?',
            'disciplina_id': disciplinas[0].id,
            'alternativas': [
                'Garantir segurança jurídica',
                'Promover a saúde e o bem estar',
                'Definir normas processuais',
                'Proteger a propriedade intelectual'
            ],
            'resposta_correta': 1,
            'explicacao': 'A nutrição tem como objetivo principal promover a saúde e o bem-estar através da alimentação adequada.',
            'dificuldade': 'facil',
            'autor_id': usuario.id
        },
        {
            'texto_questao': 'Qual tributo incide sobre produtos industrializados?',
            'disciplina_id': disciplinas[1].id,
            'alternativas': [
                'Imposto de Renda',
                'ICMS',
                'IPI',
                'ISS'
            ],
            'resposta_correta': 2,
            'explicacao': 'O IPI (Imposto sobre Produtos Industrializados) é o tributo federal que incide sobre produtos industrializados.',
            'dificuldade': 'medio',
            'autor_id': usuario.id
        },
        {
            'texto_questao': 'Quais são os macronutrientes essenciais?',
            'disciplina_id': disciplinas[0].id,
            'alternativas': [
                'Vitaminas, minerais e água',
                'Carboidratos, proteínas e lipídios',
                'Fibras, antioxidantes e probióticos',
                'Cálcio, ferro e zinco'
            ],
            'resposta_correta': 1,
            'explicacao': 'Os macronutrientes essenciais são carboidratos, proteínas e lipídios, necessários em grandes quantidades.',
            'dificuldade': 'facil',
            'autor_id': usuario.id
        }
    ]
    
    for questao_data in questoes_data:
        questao = Questao(
            texto_questao=questao_data['texto_questao'],
            disciplina_id=questao_data['disciplina_id'],
            resposta_correta=questao_data['resposta_correta'],
            explicacao=questao_data['explicacao'],
            dificuldade=questao_data['dificuldade'],
            autor_id=questao_data['autor_id']
        )
        questao.set_alternativas(questao_data['alternativas'])
        db.session.add(questao)
    
    # Criar métricas de exemplo
    for disciplina in disciplinas[:2]:  # Apenas para as duas primeiras disciplinas
        metrica = MetricaUsuario(
            usuario_id=usuario.id,
            disciplina_id=disciplina.id,
            tempo_estudo_minutos=120 if disciplina.nome == 'Nutrição' else 80,
            taxa_acertos=87.5 if disciplina.nome == 'Nutrição' else 72.0,
            dias_constancia=5 if disciplina.nome == 'Nutrição' else 2
        )
        db.session.add(metrica)
    
    db.session.commit()
    print("Dados de exemplo criados com sucesso!")
    print(f"Usuário criado: {usuario.username} (senha: 123456)")
    print(f"Disciplinas criadas: {len(disciplinas)}")
    print(f"Mapas mentais criados: {len(mapas_data)}")
    print(f"Questões criadas: {len(questoes_data)}")

if __name__ == '__main__':
    from src.main import app
    with app.app_context():
        criar_dados_exemplo()

