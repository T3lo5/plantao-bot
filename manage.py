#!/usr/bin/env python3
"""
Script de gerenciamento do bot de plantões
"""
import os
import sys
import subprocess
import argparse

def executar_comando(comando, descricao):
    """Executa um comando shell"""
    print(f"\n🔄 {descricao}...")
    resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)
    
    if resultado.returncode == 0:
        print(f"✅ {descricao} concluído!")
        if resultado.stdout:
            print(resultado.stdout)
        return True
    else:
        print(f"❌ Erro ao {descricao.lower()}")
        if resultado.stderr:
            print(resultado.stderr)
        return False

def instalar_dependencias():
    """Instala dependências do projeto"""
    return executar_comando(
        "pip install -r requirements.txt",
        "Instalando dependências"
    )

def executar_testes():
    """Executa testes do bot"""
    return executar_comando(
        "python test_bot.py",
        "Executando testes"
    )

def iniciar_bot():
    """Inicia o bot"""
    print("\n🤖 Iniciando bot...")
    print("💡 Pressione Ctrl+C para parar")
    try:
        subprocess.run(["python", "bot.py"])
    except KeyboardInterrupt:
        print("\n👋 Bot parado pelo usuário")

def iniciar_web():
    """Inicia API web"""
    print("\n🌐 Iniciando API web...")
    print("💡 Acesse: http://localhost:5000")
    print("💡 Pressione Ctrl+C para parar")
    try:
        subprocess.run(["python", "web_api.py"])
    except KeyboardInterrupt:
        print("\n👋 API web parada")

def iniciar_ambos():
    """Inicia bot e API web"""
    print("\n🚀 Iniciando bot e API web...")
    try:
        subprocess.Popen(["python", "bot.py"])
        subprocess.run(["python", "web_api.py"])
    except KeyboardInterrupt:
        print("\n👋 Serviços parados")

def criar_env():
    """Cria arquivo .env a partir do exemplo"""
    if os.path.exists('.env'):
        resposta = input("⚠️  .env já existe. Sobrescrever? (s/N): ")
        if resposta.lower() != 's':
            print("❌ Operação cancelada")
            return False
    
    if not os.path.exists('.env.example'):
        print("❌ .env.example não encontrado")
        return False
    
    with open('.env.example', 'r') as exemplo:
        conteudo = exemplo.read()
    
    with open('.env', 'w') as env:
        env.write(conteudo)
    
    print("✅ Arquivo .env criado!")
    print("💡 Edite .env com seus dados:")
    print("   - BOT_TOKEN: obtenha em @BotFather")
    print("   - CHAT_ID_NAMORADO: obtenha com /id no bot")
    return True

def limpar_banco():
    """Remove banco de dados"""
    if os.path.exists('plantoes.db'):
        resposta = input("⚠️  Isso vai apagar TODOS os plantões. Confirma? (s/N): ")
        if resposta.lower() == 's':
            os.remove('plantoes.db')
            print("✅ Banco de dados removido")
            print("💡 Será recriado automaticamente ao iniciar o bot")
            return True
        else:
            print("❌ Operação cancelada")
            return False
    else:
        print("ℹ️  Banco de dados não existe")
        return False

def backup_banco():
    """Cria backup do banco de dados"""
    if not os.path.exists('plantoes.db'):
        print("❌ Banco de dados não existe")
        return False
    
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_nome = f'plantoes_backup_{timestamp}.db'
    
    import shutil
    shutil.copy2('plantoes.db', backup_nome)
    print(f"✅ Backup criado: {backup_nome}")
    return True

def verificar_status():
    """Verifica status do bot e dependências"""
    print("\n📊 Verificando status...\n")
    
    # Verificar .env
    if os.path.exists('.env'):
        print("✅ .env configurado")
    else:
        print("❌ .env não encontrado - execute: manage.py setup")
    
    # Verificar banco
    if os.path.exists('plantoes.db'):
        import sqlite3
        conn = sqlite3.connect('plantoes.db')
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM plantoes")
        total = c.fetchone()[0]
        conn.close()
        print(f"✅ Banco de dados: {total} plantões")
    else:
        print("ℹ️  Banco de dados: não criado ainda")
    
    # Verificar dependências
    try:
        import telebot
        print("✅ pyTelegramBotAPI instalado")
    except:
        print("❌ pyTelegramBotAPI não instalado")
    
    try:
        import flask
        print("✅ Flask instalado")
    except:
        print("❌ Flask não instalado")
    
    # Verificar token
    try:
        from config import BOT_TOKEN
        if BOT_TOKEN and len(BOT_TOKEN) > 10:
            print(f"✅ Token configurado ({BOT_TOKEN[:10]}...)")
        else:
            print("⚠️  Token não configurado ou inválido")
    except:
        print("❌ Erro ao carregar configurações")

def mostrar_menu():
    """Mostra menu interativo"""
    while True:
        print("\n" + "=" * 50)
        print("🤖 BOT DE PLANTÕES MÉDICOS - GERENCIADOR")
        print("=" * 50)
        print("1. 🚀 Iniciar bot")
        print("2. 🌐 Iniciar API web")
        print("3. 🎯 Iniciar ambos (bot + web)")
        print("4. 📦 Instalar dependências")
        print("5. 🧪 Executar testes")
        print("6. ⚙️  Criar arquivo .env")
        print("7. 📊 Verificar status")
        print("8. 💾 Backup do banco")
        print("9. 🗑️  Limpar banco de dados")
        print("0. ❌ Sair")
        print("=" * 50)
        
        escolha = input("\nEscolha uma opção: ").strip()
        
        if escolha == '1':
            iniciar_bot()
        elif escolha == '2':
            iniciar_web()
        elif escolha == '3':
            iniciar_ambos()
        elif escolha == '4':
            instalar_dependencias()
        elif escolha == '5':
            executar_testes()
        elif escolha == '6':
            criar_env()
        elif escolha == '7':
            verificar_status()
        elif escolha == '8':
            backup_banco()
        elif escolha == '9':
            limpar_banco()
        elif escolha == '0':
            print("\n👋 Até logo!")
            break
        else:
            print("\n❌ Opção inválida!")

def main():
    parser = argparse.ArgumentParser(description='Gerenciador do Bot de Plantões')
    parser.add_argument('comando', nargs='?', choices=[
        'bot', 'web', 'all', 'install', 'test', 'setup', 'status', 'backup', 'clean'
    ], help='Comando a executar')
    
    args = parser.parse_args()
    
    if args.comando == 'bot':
        iniciar_bot()
    elif args.comando == 'web':
        iniciar_web()
    elif args.comando == 'all':
        iniciar_ambos()
    elif args.comando == 'install':
        instalar_dependencias()
    elif args.comando == 'test':
        executar_testes()
    elif args.comando == 'setup':
        criar_env()
    elif args.comando == 'status':
        verificar_status()
    elif args.comando == 'backup':
        backup_banco()
    elif args.comando == 'clean':
        limpar_banco()
    else:
        mostrar_menu()

if __name__ == "__main__":
    main()