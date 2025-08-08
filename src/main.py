import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.models.disciplina import Disciplina
from src.models.mapa_mental import MapaMental
from src.models.resumo import Resumo
from src.models.questao import Questao
from src.models.sessao_treinamento import SessaoTreinamento
from src.models.resposta_questao import RespostaQuestao
from src.models.metrica_usuario import MetricaUsuario

from src.routes.user import user_bp
from src.routes.disciplina import disciplina_bp
from src.routes.mapa_mental import mapa_mental_bp
from src.routes.questao import questao_bp
from src.routes.treinamento import treinamento_bp
from src.routes.metrica import metrica_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Configurar CORS para permitir requisições do frontend
CORS(app, origins="*")

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(disciplina_bp, url_prefix='/api')
app.register_blueprint(mapa_mental_bp, url_prefix='/api')
app.register_blueprint(questao_bp, url_prefix='/api')
app.register_blueprint(treinamento_bp, url_prefix='/api')
app.register_blueprint(metrica_bp, url_prefix='/api')

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # Configuração para produção
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)