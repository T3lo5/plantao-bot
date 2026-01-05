#!/usr/bin/env python3
"""
Script de diagnóstico para verificar problemas com a API web
"""
import os
import sys

print("=" * 70)
print("🔍 DIAGNÓSTICO - API WEB DO BOT DE PLANTÕES")
print("=" * 70)
print()

# 1. Verificar diretório atual
current_dir = os.getcwd()
print(f"📁 Diretório atual: {current_dir}")
print()

# 2. Listar arquivos no diretório
print("📋 Arquivos no diretório:")
try:
    files = os.listdir(current_dir)
    for f in sorted(files):
        if os.path.isdir(f):
            print(f"  📁 {f}/")
        else:
            print(f"  📄 {f}")
except Exception as e:
    print(f"  ❌ Erro: {e}")
print()

# 3. Verificar pasta static
static_path = os.path.join(current_dir, 'static')
print(f"📁 Verificando pasta static: {static_path}")
if os.path.exists(static_path):
    print("  ✅ Pasta static existe!")
    print()
    print("📋 Arquivos dentro de static/:")
    try:
        static_files = os.listdir(static_path)
        if static_files:
            for f in sorted(static_files):
                full_path = os.path.join(static_path, f)
                size = os.path.getsize(full_path)
                print(f"  📄 {f} ({size:,} bytes)")
        else:
            print("  ⚠️  Pasta static está vazia!")
    except Exception as e:
        print(f"  ❌ Erro: {e}")
else:
    print("  ❌ Pasta static NÃO existe!")
    print()
    print("💡 SOLUÇÃO:")
    print("  1. Execute: mkdir static")
    print("  2. Baixe o arquivo index.html")
    print("  3. Mova para: static/index.html")
print()

# 4. Verificar index.html especificamente
index_path = os.path.join(static_path, 'index.html')
print(f"📄 Verificando index.html: {index_path}")
if os.path.exists(index_path):
    size = os.path.getsize(index_path)
    print(f"  ✅ Arquivo existe! ({size:,} bytes)")
    
    # Verificar se tem conteúdo
    if size < 1000:
        print("  ⚠️  Arquivo muito pequeno! Pode estar vazio ou corrompido.")
    elif size > 50000:
        print("  ⚠️  Arquivo muito grande! Pode não ser o correto.")
    else:
        print("  ✅ Tamanho parece correto!")
    
    # Verificar primeiras linhas
    try:
        with open(index_path, 'r') as f:
            first_lines = [f.readline().strip() for _ in range(3)]
            print()
            print("  📝 Primeiras linhas do arquivo:")
            for i, line in enumerate(first_lines, 1):
                print(f"    {i}. {line[:60]}...")
    except:
        pass
else:
    print("  ❌ Arquivo index.html NÃO existe!")
    print()
    print("💡 SOLUÇÃO:")
    print("  1. Baixe o arquivo index.html do projeto")
    print("  2. Coloque em: static/index.html")
print()

# 5. Verificar web_api.py
web_api_path = os.path.join(current_dir, 'web_api.py')
print(f"📄 Verificando web_api.py: {web_api_path}")
if os.path.exists(web_api_path):
    print("  ✅ Arquivo web_api.py existe!")
else:
    print("  ❌ Arquivo web_api.py NÃO existe!")
print()

# 6. Verificar se Flask está instalado
print("📦 Verificando dependências:")
try:
    import flask
    print(f"  ✅ Flask instalado (versão {flask.__version__})")
except ImportError:
    print("  ❌ Flask NÃO instalado!")
    print("     Execute: pip install flask flask-cors")

try:
    import flask_cors
    print("  ✅ Flask-CORS instalado")
except ImportError:
    print("  ❌ Flask-CORS NÃO instalado!")
    print("     Execute: pip install flask-cors")
print()

# 7. Resumo e próximos passos
print("=" * 70)
print("📊 RESUMO")
print("=" * 70)

issues = []
if not os.path.exists(static_path):
    issues.append("Pasta static não existe")
if not os.path.exists(index_path):
    issues.append("Arquivo index.html não existe")

if issues:
    print("❌ PROBLEMAS ENCONTRADOS:")
    for issue in issues:
        print(f"  • {issue}")
    print()
    print("🔧 COMO RESOLVER:")
    print()
    print("1️⃣ Criar pasta static:")
    print("   mkdir static")
    print()
    print("2️⃣ Baixar index.html do projeto")
    print()
    print("3️⃣ Mover para a pasta static:")
    print("   mv ~/Downloads/index.html static/")
    print()
    print("4️⃣ Verificar novamente:")
    print("   python diagnostico.py")
    print()
    print("5️⃣ Rodar a API:")
    print("   python web_api.py")
    print()
else:
    print("✅ TUDO CERTO!")
    print()
    print("🚀 PRÓXIMOS PASSOS:")
    print("1. Execute: python web_api.py")
    print("2. Abra no navegador: http://localhost:5000")
    print("3. Digite seu Chat ID e teste!")
    print()

print("=" * 70)