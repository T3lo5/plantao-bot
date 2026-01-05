# 🤖 Bot de Plantões Médicos

Bot completo para Telegram que ajuda profissionais da saúde a gerenciar seus plantões com lembretes automáticos e interface web.

## ✨ Funcionalidades

- 📅 Adicionar plantões com data, hora e local
- ⏰ Lembretes automáticos (24h, 3h e 30min antes)
- 📱 Teclado personalizado para navegação rápida
- 🌐 Interface web para visualização
- 💾 Banco de dados SQLite persistente
- 🔔 Notificações para namorado(a)
- 🛡️ Sistema robusto com tratamento de erros

## 🚀 Deploy Gratuito (Opções)

### Opção 1: Railway.app (RECOMENDADO) 🚂

**Vantagens**: Fácil, gratuito, 500h/mês, suporta banco de dados

1. Crie conta em [railway.app](https://railway.app)
2. Clique em "New Project" → "Deploy from GitHub repo"
3. Conecte seu GitHub e selecione o repositório
4. Configure as variáveis de ambiente:
   - `BOT_TOKEN`: seu token do BotFather
   - `CHAT_ID_NAMORADO`: ID do namorado(a)
5. Deploy automático! 🎉

**Comandos Railway CLI:**
```bash
# Instalar Railway CLI
npm i -g @railway/cli

# Login
railway login

# Deploy
railway up

# Ver logs
railway logs
```

### Opção 2: Render.com 🎨

**Vantagens**: Simples, 750h/mês gratuito, SSL automático

1. Crie conta em [render.com](https://render.com)
2. New → Background Worker
3. Conecte GitHub
4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
5. Adicione variáveis de ambiente
6. Deploy! 🚀

### Opção 3: Fly.io ✈️

**Vantagens**: Muito estável, bom free tier, múltiplas regiões

```bash
# Instalar Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Criar app
fly launch --no-deploy

# Configurar secrets
fly secrets set BOT_TOKEN="seu_token"
fly secrets set CHAT_ID_NAMORADO="id"

# Deploy
fly deploy
```

### Opção 4: Google Cloud Run ☁️

**Vantagens**: Escala automática, muito confiável

```bash
# Fazer login
gcloud auth login

# Criar projeto
gcloud projects create plantao-bot

# Deploy
gcloud run deploy plantao-bot \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Opção 5: PythonAnywhere 🐍

**Vantagens**: Especializado em Python, console web

1. Crie conta free em [pythonanywhere.com](https://pythonanywhere.com)
2. Faça upload dos arquivos
3. Configure "Always-on task":
   ```
   python3 /home/seu_usuario/bot.py
   ```
4. Configure variáveis de ambiente no console

### Opção 6: Replit 🔄

**Vantagens**: IDE online, muito fácil para iniciantes

1. Crie conta em [replit.com](https://replit.com)
2. Clique em "Create Repl" → "Import from GitHub"
3. Cole URL do repositório
4. Configure Secrets (equivalente ao .env)
5. Clique em "Run"

### Opção 7: Oracle Cloud (Always Free) 💪

**Vantagens**: REALMENTE gratuito para sempre, VPS completa

1. Crie conta em [oracle.com/cloud/free](https://oracle.com/cloud/free)
2. Crie instância Compute (VM.Standard.E2.1.Micro)
3. Conecte via SSH e execute:

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python e Git
sudo apt install python3 python3-pip git -y

# Clonar repositório
git clone https://github.com/seu-usuario/plantao-bot.git
cd plantao-bot

# Instalar dependências
pip3 install -r requirements.txt

# Configurar .env
nano .env
# Cole: BOT_TOKEN=seu_token

# Rodar com screen (mantém rodando)
screen -S bot
python3 bot.py
# Ctrl+A+D para desatachar
```

## 📦 Instalação Local

```bash
# Clonar repositório
git clone https://github.com/seu-usuario/plantao-bot.git
cd plantao-bot

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis
cp .env.example .env
nano .env  # Edite com seus dados

# Rodar bot
python bot.py

# Rodar API web (terminal separado)
python web_api.py
```

## 🐳 Deploy com Docker

```bash
# Build
docker build -t plantao-bot .

# Rodar bot
docker run -d --name plantao-bot \
  -e BOT_TOKEN="seu_token" \
  -e CHAT_ID_NAMORADO="id" \
  -v $(pwd)/data:/app/data \
  plantao-bot

# Rodar tudo (bot + web)
docker-compose up -d
```

## 🔑 Obter Token do Bot

1. Abra [@BotFather](https://t.me/BotFather) no Telegram
2. Envie `/newbot`
3. Escolha um nome e username
4. Copie o token fornecido

## 📱 Obter Chat ID

1. Inicie o bot
2. Envie `/start`
3. Envie `/id`
4. Copie o número fornecido

## 🌐 Interface Web

Após deploy, acesse: `https://seu-app.railway.app` (ou URL da sua plataforma)

**Features da interface:**
- ✅ Visualização de todos os plantões
- 📊 Estatísticas (total, hoje, amanhã)
- 🎨 Design moderno e responsivo
- 💾 Salva Chat ID no localStorage

## 📁 Estrutura do Projeto

```
plantao-bot/
├── bot.py              # Bot principal
├── config.py           # Configurações
├── database.py         # Gerenciamento do banco
├── lembretes.py        # Sistema de lembretes
├── keyboards.py        # Teclados do Telegram
├── utils.py            # Funções auxiliares
├── web_api.py          # API Flask
├── static/
│   └── index.html      # Interface web
├── requirements.txt    # Dependências
├── Dockerfile          # Container Docker
├── docker-compose.yml  # Orquestração
├── Procfile           # Deploy Heroku/Railway
├── railway.json        # Config Railway
├── runtime.txt         # Versão Python
└── .env.example        # Exemplo de variáveis
```

## ⚙️ Variáveis de Ambiente

```env
# Obrigatórias
BOT_TOKEN=seu_token_do_botfather
CHAT_ID_NAMORADO=id_do_namorado  # Opcional

# Opcionais
FLASK_PORT=5000
FLASK_DEBUG=False
DATABASE_NAME=plantoes.db
```

## 🔧 Comandos do Bot

```
/start      - Menu inicial
/plantao    - Adicionar plantão
/hoje       - Plantões de hoje
/amanha     - Plantões de amanhã
/proximos   - Próximos 5 plantões
/todos      - Todos os plantões
/debug      - Informações técnicas
/id         - Mostra Chat ID
/ajuda      - Ajuda
```

## 🎨 Customização

### Alterar lembretes:

Edite `config.py`:
```python
LEMBRETE_24H = 24  # horas
LEMBRETE_3H = 3
LEMBRETE_30MIN = 0.5
```

### Adicionar novos comandos:

Edite `bot.py`:
```python
@bot.message_handler(commands=['meucomando'])
def meu_comando(message):
    bot.send_message(message.chat.id, "Olá!")
```

## 🐛 Troubleshooting

### Bot não responde:
```bash
# Verificar logs
python bot.py  # Ver output

# Testar conexão
python -c "import telebot; bot = telebot.TeleBot('TOKEN'); print(bot.get_me())"
```

### Lembretes não funcionam:
- Verifique se a data/hora está no formato correto
- Use `/debug` para ver status dos lembretes
- Verifique logs do servidor

### Banco de dados corrompido:
```bash
rm plantoes.db
python bot.py  # Recria automaticamente
```

## 📊 Monitoramento

### Logs em Railway:
```bash
railway logs
```

### Logs em Render:
- Acesse dashboard → Logs

### Logs em Docker:
```bash
docker logs plantao-bot -f
```

## 🔒 Segurança

- ✅ Nunca commite `.env` no Git
- ✅ Use variáveis de ambiente em produção
- ✅ Mantenha token do bot secreto
- ✅ Atualize dependências regularmente:
  ```bash
  pip install -r requirements.txt --upgrade
  ```

## 🆘 Suporte

- 📧 Email: seu@email.com
- 💬 Telegram: @seu_usuario
- 🐛 Issues: [GitHub Issues](https://github.com/seu-usuario/plantao-bot/issues)

## 📝 Licença

MIT License - use à vontade!

## 🎯 Roadmap

- [ ] Exportar plantões para Google Calendar
- [ ] Notificações push
- [ ] Multi-idioma
- [ ] Estatísticas avançadas
- [ ] Integração com WhatsApp
- [ ] App mobile nativo

## ❤️ Agradecimentos

Feito com amor para facilitar a vida dos profissionais da saúde! 👩‍⚕️👨‍⚕️

---

**💡 Dica**: Para melhor experiência, use Railway.app para deploy gratuito 24/7!