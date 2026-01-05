"""
Configurações do Bot de Plantões Médicos
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Configurações do Bot
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID_NAMORADO = os.getenv('CHAT_ID_NAMORADO', '')  

# Validação: Token é obrigatório
if not BOT_TOKEN:
    print("❌ ERRO: BOT_TOKEN não encontrado!")
    print("💡 Crie um arquivo .env na raiz do projeto com:")
    print("   BOT_TOKEN=seu_token_aqui")
    print("\n📝 Obtenha seu token em: https://t.me/BotFather")
    sys.exit(1)

# Configurações do Banco de Dados
DATABASE_NAME = 'plantoes.db'

# Configurações de Lembretes (em horas)
LEMBRETE_24H = 24
LEMBRETE_3H = 3
LEMBRETE_30MIN = 0.5

# Tolerância para verificação de lembretes (em horas)
TOLERANCIA_24H = 0.5
TOLERANCIA_3H = 0.25
TOLERANCIA_30MIN = 0.17

# Intervalo de verificação de lembretes (em segundos)
INTERVALO_VERIFICACAO = 60

# Configurações de Logging
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'