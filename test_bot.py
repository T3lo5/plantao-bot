"""
Script de testes para o bot de plantões
"""
import sqlite3
import sys
from datetime import datetime, timedelta

def teste_banco_dados():
    """Testa criação e operações do banco"""
    print("🧪 Testando banco de dados...")
    
    try:
        from database import Database
        
        # Inicializar banco
        Database.init_db()
        print("  ✅ Banco inicializado")
        
        # Testar inserção
        chat_id_teste = 123456789
        data_teste = "15/03"
        hora_teste = "19:00"
        local_teste = "Hospital Teste"
        
        plantao_id = Database.salvar_plantao(chat_id_teste, data_teste, hora_teste, local_teste)
        print(f"  ✅ Plantão salvo (ID: {plantao_id})")
        
        # Testar busca
        plantoes = Database.buscar_plantoes_por_data(chat_id_teste, data_teste)
        assert len(plantoes) > 0, "Nenhum plantão encontrado"
        print(f"  ✅ Plantão encontrado: {plantoes[0]}")
        
        # Limpar teste
        conn = sqlite3.connect('plantoes.db')
        c = conn.cursor()
        c.execute("DELETE FROM plantoes WHERE chat_id = ?", (chat_id_teste,))
        conn.commit()
        conn.close()
        print("  ✅ Dados de teste removidos")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False

def teste_utils():
    """Testa funções utilitárias"""
    print("\n🧪 Testando utilitários...")
    
    try:
        from utils import DateTimeUtils, validar_formato_plantao
        
        # Testar validação de data
        assert DateTimeUtils.validar_data("15/03"), "Data válida rejeitada"
        assert not DateTimeUtils.validar_data("32/13"), "Data inválida aceita"
        print("  ✅ Validação de data funciona")
        
        # Testar validação de hora
        assert DateTimeUtils.validar_hora("19:00"), "Hora válida rejeitada"
        assert not DateTimeUtils.validar_hora("25:00"), "Hora inválida aceita"
        print("  ✅ Validação de hora funciona")
        
        # Testar parse de data/hora
        data_plantao = DateTimeUtils.parse_data_hora("15/03", "19:00")
        assert data_plantao is not None, "Parse falhou"
        print(f"  ✅ Parse de data/hora funciona: {data_plantao}")
        
        # Testar cálculo de tempo
        horas, status = DateTimeUtils.calcular_tempo_restante(data_plantao)
        print(f"  ✅ Cálculo de tempo: {status}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False

def teste_config():
    """Testa configurações"""
    print("\n🧪 Testando configurações...")
    
    try:
        from config import BOT_TOKEN, LEMBRETE_24H, LEMBRETE_3H, LEMBRETE_30MIN
        
        assert BOT_TOKEN, "Token não configurado"
        print(f"  ✅ Token configurado (primeiros chars: {BOT_TOKEN[:10]}...)")
        
        assert LEMBRETE_24H == 24, "Lembrete 24h incorreto"
        assert LEMBRETE_3H == 3, "Lembrete 3h incorreto"
        assert LEMBRETE_30MIN == 0.5, "Lembrete 30min incorreto"
        print("  ✅ Configurações de lembretes corretas")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False

def teste_bot_conexao():
    """Testa conexão com API do Telegram"""
    print("\n🧪 Testando conexão com Telegram...")
    
    try:
        import telebot
        from config import BOT_TOKEN
        
        bot = telebot.TeleBot(BOT_TOKEN)
        info = bot.get_me()
        
        print(f"  ✅ Conectado como: @{info.username}")
        print(f"  ✅ Nome: {info.first_name}")
        print(f"  ✅ ID: {info.id}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        print("  💡 Verifique se o token está correto no .env")
        return False

def teste_estrutura_arquivos():
    """Verifica se todos os arquivos necessários existem"""
    print("\n🧪 Testando estrutura de arquivos...")
    
    arquivos_necessarios = [
        'bot.py',
        'config.py',
        'database.py',
        'lembretes.py',
        'keyboards.py',
        'utils.py',
        'web_api.py',
        'requirements.txt',
        'README.md'
    ]
    
    import os
    
    todos_existem = True
    for arquivo in arquivos_necessarios:
        if os.path.exists(arquivo):
            print(f"  ✅ {arquivo}")
        else:
            print(f"  ❌ {arquivo} - NÃO ENCONTRADO")
            todos_existem = False
    
    return todos_existem

def teste_dependencias():
    """Testa se todas as dependências estão instaladas"""
    print("\n🧪 Testando dependências...")
    
    dependencias = [
        'telebot',
        'flask',
        'flask_cors',
        'dotenv'
    ]
    
    todas_instaladas = True
    for dep in dependencias:
        try:
            __import__(dep)
            print(f"  ✅ {dep}")
        except ImportError:
            print(f"  ❌ {dep} - NÃO INSTALADO")
            todas_instaladas = False
    
    return todas_instaladas

def executar_todos_testes():
    """Executa todos os testes"""
    print("=" * 70)
    print("🧪 EXECUTANDO TESTES DO BOT DE PLANTÕES")
    print("=" * 70)
    
    resultados = {
        "Estrutura de arquivos": teste_estrutura_arquivos(),
        "Dependências": teste_dependencias(),
        "Configurações": teste_config(),
        "Banco de dados": teste_banco_dados(),
        "Utilitários": teste_utils(),
        "Conexão Telegram": teste_bot_conexao()
    }
    
    print("\n" + "=" * 70)
    print("📊 RESULTADO DOS TESTES")
    print("=" * 70)
    
    todos_passaram = True
    for teste, resultado in resultados.items():
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"{status} - {teste}")
        if not resultado:
            todos_passaram = False
    
    print("=" * 70)
    
    if todos_passaram:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Bot está pronto para uso!")
        return 0
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        print("💡 Corrija os erros antes de fazer deploy")
        return 1

if __name__ == "__main__":
    sys.exit(executar_todos_testes())