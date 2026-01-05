"""
API Web para consultar plantões
"""
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
from database import Database, get_db_connection
from utils import DateTimeUtils
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar caminho da pasta static
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_FOLDER = os.path.join(BASE_DIR, 'static')

# Criar pasta static se não existir
if not os.path.exists(STATIC_FOLDER):
    os.makedirs(STATIC_FOLDER)
    logger.warning(f"⚠️  Pasta static não encontrada. Criada em: {STATIC_FOLDER}")
    logger.warning("💡 Coloque o arquivo index.html dentro da pasta static!")

app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path='')
CORS(app)

# Inicializar banco
Database.init_db()

@app.route('/')
def index():
    """Página principal"""
    logger.info(f"📥 Requisição recebida para /")
    logger.info(f"📁 Procurando em: {STATIC_FOLDER}")
    logger.info(f"📄 Arquivo: {os.path.join(STATIC_FOLDER, 'index.html')}")
    
    index_file = os.path.join(STATIC_FOLDER, 'index.html')
    
    if not os.path.exists(STATIC_FOLDER):
        logger.error(f"❌ Pasta static não existe: {STATIC_FOLDER}")
        return criar_pagina_erro("Pasta static não encontrada", STATIC_FOLDER)
    
    if not os.path.exists(index_file):
        logger.error(f"❌ index.html não existe: {index_file}")
        # Listar o que tem na pasta
        try:
            files = os.listdir(STATIC_FOLDER)
            logger.info(f"📋 Arquivos em static/: {files}")
        except:
            pass
        return criar_pagina_erro("index.html não encontrado", STATIC_FOLDER)
    
    try:
        logger.info("✅ Servindo index.html")
        return send_from_directory(STATIC_FOLDER, 'index.html')
    except Exception as e:
        logger.error(f"❌ Erro ao servir arquivo: {e}")
        return criar_pagina_erro(f"Erro ao carregar: {e}", STATIC_FOLDER)

def criar_pagina_erro(motivo, caminho):
    """Cria página de erro explicativa"""
    return f"""
    <html>
    <head>
        <title>Erro - Bot de Plantões</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }}
            .error-box {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{ color: #d32f2f; }}
            code {{
                background: #f0f0f0;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: monospace;
            }}
            .success {{ color: #2e7d32; }}
            .error {{ color: #d32f2f; }}
            ol {{ text-align: left; }}
            li {{ margin: 10px 0; }}
        </style>
    </head>
    <body>
        <div class="error-box">
            <h1>⚠️ Erro: {motivo}</h1>
            
            <h2>Informações de Debug:</h2>
            <ul>
                <li><strong>Pasta static esperada:</strong> <code>{caminho}</code></li>
                <li><strong>Arquivo esperado:</strong> <code>{os.path.join(caminho, 'index.html')}</code></li>
            </ul>
            
            <h2>Como resolver:</h2>
            <ol>
                <li>Abra o terminal na pasta do projeto</li>
                <li>Execute: <code>python diagnostico.py</code></li>
                <li>Siga as instruções</li>
            </ol>
            
            <h2>Ou manualmente:</h2>
            <ol>
                <li>Crie a pasta: <code>mkdir static</code></li>
                <li>Baixe o arquivo <code>index.html</code></li>
                <li>Mova para: <code>static/index.html</code></li>
                <li>Reinicie o servidor</li>
            </ol>
            
            <h2>Enquanto isso, a API funciona:</h2>
            <ul>
                <li><a href="/api/health">GET /api/health</a> - Testar API</li>
                <li>GET /api/plantoes/{{chat_id}} - Buscar plantões</li>
                <li>GET /api/stats/{{chat_id}} - Estatísticas</li>
            </ul>
        </div>
    </body>
    </html>
    """, 404

@app.route('/api/plantoes/<int:chat_id>', methods=['GET'])
def get_plantoes(chat_id):
    """Retorna plantões de um usuário"""
    try:
        limite = request.args.get('limite', 10, type=int)
        plantoes = Database.buscar_proximos_plantoes(chat_id, limite)
        
        resultado = []
        for data, hora, local in plantoes:
            data_plantao = DateTimeUtils.parse_data_hora(data, hora)
            if data_plantao:
                horas_restantes, status = DateTimeUtils.calcular_tempo_restante(data_plantao)
                resultado.append({
                    'data': data,
                    'hora': hora,
                    'local': local,
                    'status': status,
                    'horas_restantes': round(horas_restantes, 2)
                })
        
        return jsonify({
            'success': True,
            'total': len(resultado),
            'plantoes': resultado
        })
    
    except Exception as e:
        logger.error(f"Erro ao buscar plantões: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/plantoes/<int:chat_id>/hoje', methods=['GET'])
def get_plantoes_hoje(chat_id):
    """Retorna plantões de hoje"""
    try:
        hoje = DateTimeUtils.obter_data_hoje()
        plantoes = Database.buscar_plantoes_por_data(chat_id, hoje)
        
        resultado = [{
            'data': data,
            'hora': hora,
            'local': local
        } for data, hora, local in plantoes]
        
        return jsonify({
            'success': True,
            'data': hoje,
            'total': len(resultado),
            'plantoes': resultado
        })
    
    except Exception as e:
        logger.error(f"Erro ao buscar plantões de hoje: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/plantoes/<int:chat_id>/amanha', methods=['GET'])
def get_plantoes_amanha(chat_id):
    """Retorna plantões de amanhã"""
    try:
        amanha = DateTimeUtils.obter_data_amanha()
        plantoes = Database.buscar_plantoes_por_data(chat_id, amanha)
        
        resultado = [{
            'data': data,
            'hora': hora,
            'local': local
        } for data, hora, local in plantoes]
        
        return jsonify({
            'success': True,
            'data': amanha,
            'total': len(resultado),
            'plantoes': resultado
        })
    
    except Exception as e:
        logger.error(f"Erro ao buscar plantões de amanhã: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats/<int:chat_id>', methods=['GET'])
def get_stats(chat_id):
    """Retorna estatísticas do usuário"""
    try:
        total = Database.contar_plantoes(chat_id)
        hoje = DateTimeUtils.obter_data_hoje()
        amanha = DateTimeUtils.obter_data_amanha()
        
        plantoes_hoje = len(Database.buscar_plantoes_por_data(chat_id, hoje))
        plantoes_amanha = len(Database.buscar_plantoes_por_data(chat_id, amanha))
        
        return jsonify({
            'success': True,
            'stats': {
                'total_plantoes': total,
                'plantoes_hoje': plantoes_hoje,
                'plantoes_amanha': plantoes_amanha
            }
        })
    
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de health check"""
    return jsonify({
        'status': 'ok',
        'message': 'API funcionando'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)