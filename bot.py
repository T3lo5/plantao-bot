"""
Bot de Plantões Médicos - Versão Refatorada
"""
import logging
import telebot
from telebot import types
from datetime import datetime

from config import BOT_TOKEN, CHAT_ID_NAMORADO, LOG_LEVEL, LOG_FORMAT
from database import Database
from keyboards import KeyboardFactory
from lembretes import LembreteService, enviar_notificacao_namorado
from utils import DateTimeUtils, MessageFormatter, validar_formato_plantao

# Configurar logging
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

# Inicializar bot
bot = telebot.TeleBot(BOT_TOKEN)

# Inicializar banco de dados
Database.init_db()

# Inicializar serviço de lembretes
lembrete_service = LembreteService(bot)


# ========== HANDLERS DE COMANDOS ==========

@bot.message_handler(commands=['start', 'ajuda', 'help'])
def cmd_start(message):
    """Comando /start - Menu inicial"""
    welcome_text = """
👨‍⚕️ *BOT DE PLANTÕES MÉDICOS* 👩‍⚕️

*Use os botões abaixo ou comandos:*

• /plantao - Adicionar plantão
• /hoje - Plantões hoje  
• /amanha - Plantões amanhã
• /proximos - Próximos plantões
• /todos - Todos os plantões
• /deletar - Deletar plantão
• /debug - Informações técnicas
• /id - Mostra seu Chat ID

*FORMATO RÁPIDO:*
`/plantao DD/MM HH:MM Hospital`

*Exemplo:*
`/plantao 15/03 19:00 Hospital Evangélico`

⏰ *Lembretes automáticos:*
   • 24 horas antes
   • 3 horas antes  
   • 30 minutos antes

💡 Use os botões para navegação rápida!
"""
    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode='Markdown',
        reply_markup=KeyboardFactory.criar_teclado_principal()
    )


@bot.message_handler(commands=['plantao'])
def cmd_plantao(message):
    """Comando /plantao - Adicionar novo plantão"""
    partes = message.text.split(' ', 3)
    
    # Formato completo: /plantao DD/MM HH:MM Local
    if len(partes) >= 4:
        valido, erro = validar_formato_plantao(partes)
        
        if not valido:
            bot.send_message(message.chat.id, erro, parse_mode='Markdown')
            return
        
        data_str = partes[1]
        hora_str = partes[2]
        local = partes[3]
        
        _salvar_e_confirmar_plantao(message.chat.id, data_str, hora_str, local)
    
    # Formato interativo
    else:
        msg = bot.send_message(
            message.chat.id,
            "📅 *Envie a data e hora do plantão:*\n\nFormato: DD/MM HH:MM\nExemplo: 15/03 19:00",
            parse_mode='Markdown',
            reply_markup=KeyboardFactory.criar_teclado_data_hora()
        )
        bot.register_next_step_handler(msg, _processar_data_hora)


def _processar_data_hora(message):
    """Processa entrada de data/hora no modo interativo"""
    if message.text == "❌ Cancelar":
        bot.send_message(
            message.chat.id,
            "❌ Operação cancelada.",
            reply_markup=KeyboardFactory.criar_teclado_principal()
        )
        return
    
    try:
        partes = message.text.split()
        if len(partes) != 2:
            raise ValueError("Formato inválido")
        
        data_str, hora_str = partes
        
        if not DateTimeUtils.validar_data(data_str):
            raise ValueError("Data inválida")
        
        if not DateTimeUtils.validar_hora(hora_str):
            raise ValueError("Hora inválida")
        
        msg = bot.send_message(
            message.chat.id,
            "🏥 *Agora digite o local do plantão:*",
            parse_mode='Markdown',
            reply_markup=KeyboardFactory.criar_teclado_locais()
        )
        bot.register_next_step_handler(msg, lambda m: _processar_local(m, data_str, hora_str))
        
    except Exception as e:
        bot.send_message(
            message.chat.id,
            "❌ Formato inválido. Use: DD/MM HH:MM\nExemplo: 15/03 19:00",
            reply_markup=KeyboardFactory.criar_teclado_principal()
        )


def _processar_local(message, data_str, hora_str):
    """Processa entrada de local no modo interativo"""
    if message.text == "❌ Cancelar":
        bot.send_message(
            message.chat.id,
            "❌ Operação cancelada.",
            reply_markup=KeyboardFactory.criar_teclado_principal()
        )
        return
    
    # Se escolheu "Outro local", pede para digitar
    if message.text == "📍 Outro local":
        msg = bot.send_message(
            message.chat.id,
            "📝 *Digite o nome do local:*",
            parse_mode='Markdown'
        )
        bot.register_next_step_handler(msg, lambda m: _processar_local_customizado(m, data_str, hora_str))
        return
    
    local = message.text
    _salvar_e_confirmar_plantao(message.chat.id, data_str, hora_str, local)


def _processar_local_customizado(message, data_str, hora_str):
    """Processa local customizado digitado pelo usuário"""
    if message.text == "❌ Cancelar":
        bot.send_message(
            message.chat.id,
            "❌ Operação cancelada.",
            reply_markup=KeyboardFactory.criar_teclado_principal()
        )
        return
    
    local = message.text
    _salvar_e_confirmar_plantao(message.chat.id, data_str, hora_str, local)


def _salvar_e_confirmar_plantao(chat_id, data_str, hora_str, local):
    """Salva plantão e envia confirmação"""
    try:
        plantao_id = Database.salvar_plantao(chat_id, data_str, hora_str, local)
        
        # Calcular data completa para mostrar o ano
        data_plantao = DateTimeUtils.parse_data_hora(data_str, hora_str)
        ano_str = f" ({data_plantao.year})" if data_plantao else ""
        
        resposta = f"""
✅ *PLANTÃO SALVO COM SUCESSO!*

📅 *Data:* {data_str}{ano_str}
⏰ *Hora:* {hora_str}
🏥 *Local:* {local}

📱 *Lembretes automáticos:*
   ⏰ 24 horas antes
   🔔 3 horas antes
   🚨 30 minutos antes

💡 *Dica:* Já separou tudo que precisa?
"""
        
        bot.send_message(
            chat_id,
            resposta,
            parse_mode='Markdown',
            reply_markup=KeyboardFactory.criar_teclado_principal()
        )
        
        # Notifica namorado
        enviar_notificacao_namorado(bot, CHAT_ID_NAMORADO, data_str, hora_str, local)
        
    except Exception as e:
        logger.error(f"Erro ao salvar plantão: {e}")
        bot.send_message(
            chat_id,
            f"❌ *Erro ao salvar plantão:* {str(e)}",
            parse_mode='Markdown',
            reply_markup=KeyboardFactory.criar_teclado_principal()
        )


@bot.message_handler(commands=['hoje'])
def cmd_hoje(message):
    """Comando /hoje - Mostra plantões de hoje"""
    hoje = DateTimeUtils.obter_data_hoje()
    plantoes = Database.buscar_plantoes_por_data(message.chat.id, hoje)
    
    if plantoes:
        resposta = "📅 *PLANTÕES DE HOJE:*\n\n"
        for data, hora, local in plantoes:
            resposta += f"⏰ *{hora}* - {local}\n"
    else:
        resposta = "✅ Nenhum plantão hoje! Aproveite o descanso! 😊"
    
    bot.send_message(
        message.chat.id,
        resposta,
        parse_mode='Markdown',
        reply_markup=KeyboardFactory.criar_teclado_principal()
    )


@bot.message_handler(commands=['amanha'])
def cmd_amanha(message):
    """Comando /amanhã - Mostra plantões de amanhã"""
    amanha = DateTimeUtils.obter_data_amanha()
    plantoes = Database.buscar_plantoes_por_data(message.chat.id, amanha)
    
    if plantoes:
        resposta = "📅 *PLANTÕES DE AMANHÃ:*\n\n"
        for data, hora, local in plantoes:
            resposta += f"⏰ *{hora}* - {local}\n"
    else:
        resposta = "✅ Nenhum plantão amanhã! 🎉"
    
    bot.send_message(
        message.chat.id,
        resposta,
        parse_mode='Markdown',
        reply_markup=KeyboardFactory.criar_teclado_principal()
    )


@bot.message_handler(commands=['proximos'])
def cmd_proximos(message):
    """Comando /proximos - Mostra próximos 5 plantões"""
    plantoes = Database.buscar_proximos_plantoes(message.chat.id, 5)
    
    if plantoes:
        resposta = MessageFormatter.formatar_lista_plantoes(plantoes, "📋 *PRÓXIMOS PLANTÕES:*")
    else:
        resposta = "📭 Nenhum plantão agendado ainda.\nUse /plantao para adicionar!"
    
    bot.send_message(
        message.chat.id,
        resposta,
        parse_mode='Markdown',
        reply_markup=KeyboardFactory.criar_teclado_principal()
    )


@bot.message_handler(commands=['todos'])
def cmd_todos(message):
    """Comando /todos - Mostra todos os plantões"""
    plantoes = Database.buscar_proximos_plantoes(message.chat.id, 100)
    
    if plantoes:
        resposta = MessageFormatter.formatar_lista_plantoes(plantoes, "📋 *TODOS OS PLANTÕES:*")
        if len(plantoes) > 10:
            resposta += f"\n\n📊 *Total:* {len(plantoes)} plantões"
    else:
        resposta = "📭 Nenhum plantão agendado ainda."
    
    bot.send_message(
        message.chat.id,
        resposta,
        parse_mode='Markdown',
        reply_markup=KeyboardFactory.criar_teclado_principal()
    )


@bot.message_handler(commands=['id'])
def cmd_id(message):
    """Comando /id - Mostra Chat ID do usuário"""
    bot.send_message(
        message.chat.id,
        f"🔑 *Seu Chat ID:* `{message.chat.id}`\n\nEnvie este número para configurar notificações!",
        parse_mode='Markdown',
        reply_markup=KeyboardFactory.criar_teclado_principal()
    )


@bot.message_handler(commands=['debug'])
def cmd_debug(message):
    """Comando /debug - Informações técnicas"""
    agora = datetime.now()
    total = Database.contar_plantoes()
    meus_plantoes = Database.contar_plantoes(message.chat.id)
    proximos = Database.buscar_proximos_plantoes(message.chat.id, 5)
    
    resposta = f"""
🔧 *INFORMAÇÕES DE DEBUG:*

⏰ Hora do servidor: {agora.strftime('%d/%m/%Y %H:%M:%S')}
📊 Total de plantões: {total}
👤 Seus plantões: {meus_plantoes}
🤖 Bot: @PlantaoMedBot
🔑 Seu Chat ID: `{message.chat.id}`

📋 *Seus próximos plantões:*
"""
    
    for data, hora, local in proximos:
        data_plantao = DateTimeUtils.parse_data_hora(data, hora)
        if data_plantao:
            horas_restantes, status = DateTimeUtils.calcular_tempo_restante(data_plantao)
            # Mostrar ano também para debug
            ano = data_plantao.year
            resposta += f"\n📅 *{data}/{ano} {hora}* - {local}\n   {status}\n"
    
    resposta += "\n💡 *Dica:* Se o ano estiver errado, use /corrigir_ano"
    
    bot.send_message(
        message.chat.id,
        resposta,
        parse_mode='Markdown',
        reply_markup=KeyboardFactory.criar_teclado_principal()
    )


@bot.message_handler(commands=['corrigir_ano'])
def cmd_corrigir_ano(message):
    """Comando para corrigir ano de plantões que foram interpretados errado"""
    bot.send_message(
        message.chat.id,
        """
🔧 *CORREÇÃO DE ANO*

Se algum plantão foi cadastrado com ano errado, você tem 2 opções:

*Opção 1 - Deletar e recriar:*
1. Use /deletar para remover o plantão errado
2. Adicione novamente com /plantao

*Opção 2 - Editar banco (avançado):*
Use /debug para ver os anos dos plantões.

💡 *Dica para evitar o problema:*
• Plantões do ano atual: cadastre normalmente
• Plantões de 2027 em diante: por enquanto use /deletar e recrie quando estiver mais próximo

🤖 *Como funciona:*
O bot assume que:
• Datas futuras = ano atual
• Datas que passaram há pouco (até 6 meses) = ano atual (plantão já aconteceu)
• Datas que passaram há muito (mais de 6 meses) = ano que vem
        """,
        parse_mode='Markdown',
        reply_markup=KeyboardFactory.criar_teclado_principal()
    )


@bot.message_handler(commands=['limpar_lembretes'])
def cmd_limpar_lembretes(message):
    """Comando /limpar_lembretes - Reseta status de lembretes (útil para testes)"""
    try:
        import sqlite3
        conn = sqlite3.connect('plantoes.db')
        c = conn.cursor()
        c.execute('''UPDATE plantoes 
                     SET lembrete_24h = 0, lembrete_3h = 0, lembrete_30min = 0 
                     WHERE chat_id = ?''', (message.chat.id,))
        conn.commit()
        conn.close()
        
        bot.send_message(
            message.chat.id,
            "✅ *Lembretes resetados!*\n\nTodos os lembretes foram marcados como não enviados.",
            parse_mode='Markdown',
            reply_markup=KeyboardFactory.criar_teclado_principal()
        )
        logger.info(f"🔄 Lembretes resetados para usuário {message.chat.id}")
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Erro ao resetar lembretes: {e}",
            reply_markup=KeyboardFactory.criar_teclado_principal()
        )


@bot.message_handler(commands=['deletar'])
def cmd_deletar(message):
    """Comando /deletar - Lista plantões para deletar"""
    plantoes = Database.buscar_proximos_plantoes(message.chat.id, 10)
    
    if not plantoes:
        bot.send_message(
            message.chat.id,
            "📭 Você não tem plantões agendados para deletar.",
            reply_markup=KeyboardFactory.criar_teclado_principal()
        )
        return
    
    # Buscar IDs dos plantões para criar botões
    import sqlite3
    conn = sqlite3.connect('plantoes.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''SELECT id, data, hora, local FROM plantoes 
                 WHERE chat_id = ? AND ativo = 1
                 ORDER BY substr(data, 4, 2) || substr(data, 1, 2), hora
                 LIMIT 10''', (message.chat.id,))
    plantoes_completos = c.fetchall()
    conn.close()
    
    # Criar botões inline para cada plantão
    markup = types.InlineKeyboardMarkup()
    for plantao in plantoes_completos:
        texto_botao = f"🗑️ {plantao['data']} {plantao['hora']} - {plantao['local'][:20]}"
        markup.add(types.InlineKeyboardButton(
            texto_botao,
            callback_data=f"delete_{plantao['id']}"
        ))
    
    markup.add(types.InlineKeyboardButton("❌ Cancelar", callback_data="cancel_delete"))
    
    bot.send_message(
        message.chat.id,
        "🗑️ *DELETAR PLANTÃO*\n\nSelecione o plantão que deseja remover:",
        parse_mode='Markdown',
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_') or call.data == 'cancel_delete')
def callback_deletar(call):
    """Handler para os botões de deletar"""
    if call.data == 'cancel_delete':
        bot.edit_message_text(
            "❌ Operação cancelada.",
            call.message.chat.id,
            call.message.message_id
        )
        bot.answer_callback_query(call.id)
        return
    
    # Extrair ID do plantão
    plantao_id = int(call.data.split('_')[1])
    
    # Buscar dados do plantão antes de deletar
    import sqlite3
    conn = sqlite3.connect('plantoes.db')
    c = conn.cursor()
    c.execute("SELECT data, hora, local FROM plantoes WHERE id = ? AND chat_id = ?",
              (plantao_id, call.message.chat.id))
    plantao = c.fetchone()
    
    if not plantao:
        bot.answer_callback_query(call.id, "❌ Plantão não encontrado!")
        return
    
    # Deletar plantão
    Database.desativar_plantao(plantao_id)
    conn.close()
    
    data, hora, local = plantao
    
    # Atualizar mensagem
    bot.edit_message_text(
        f"✅ *PLANTÃO DELETADO!*\n\n"
        f"📅 {data} ⏰ {hora}\n"
        f"🏥 {local}\n\n"
        f"O plantão foi removido com sucesso.",
        call.message.chat.id,
        call.message.message_id,
        parse_mode='Markdown'
    )
    
    bot.answer_callback_query(call.id, "✅ Plantão deletado!")
    logger.info(f"🗑️ Plantão {plantao_id} deletado pelo usuário {call.message.chat.id}")


# ========== HANDLER DE BOTÕES DO TECLADO ==========

@bot.message_handler(func=lambda message: True)
def handle_keyboard(message):
    """Processa cliques nos botões do teclado"""
    texto = message.text
    
    handlers = {
        "➕ Plantão": lambda: _mostrar_ajuda_plantao(message),
        "📅 Hoje": lambda: cmd_hoje(message),
        "📆 Amanhã": lambda: cmd_amanha(message),
        "📋 Próximos": lambda: cmd_proximos(message),
        "🗑️ Deletar": lambda: cmd_deletar(message),
        "🔧 Debug": lambda: cmd_debug(message),
        "❓ Ajuda": lambda: cmd_start(message)
    }
    
    handler = handlers.get(texto)
    if handler:
        handler()
    elif not texto.startswith('/'):
        bot.send_message(
            message.chat.id,
            "🤔 *Não entendi!*\n\nUse os botões abaixo ou comandos como:\n`/plantao 15/03 19:00 Hospital`",
            parse_mode='Markdown',
            reply_markup=KeyboardFactory.criar_teclado_principal()
        )


def _mostrar_ajuda_plantao(message):
    """Mostra ajuda para adicionar plantão"""
    bot.send_message(
        message.chat.id,
        "📝 *Para adicionar plantão:*\n\n"
        "`/plantao DD/MM HH:MM Hospital`\n\n"
        "*Exemplo:*\n"
        "`/plantao 15/03 19:00 Hospital Albert Einstein`\n\n"
        "Ou clique em ➕ Plantão e siga as instruções!",
        parse_mode='Markdown',
        reply_markup=KeyboardFactory.criar_teclado_principal()
    )


# ========== INICIALIZAÇÃO ==========

def main():
    """Função principal"""
    print("=" * 70)
    print("🤖 BOT DE PLANTÕES MÉDICOS - VERSÃO PROFISSIONAL")
    print("=" * 70)
    print(f"⏰ Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"📱 Teclado personalizado: ✅")
    print(f"🛡️ Sistema de lembretes: ✅")
    print(f"💾 Banco de dados: ✅")
    print("=" * 70)
    
    try:
        # Testa conexão
        bot_info = bot.get_me()
        print(f"✅ Conectado como: @{bot_info.username}")
        print(f"📛 Nome: {bot_info.first_name}")
        
        # Inicia serviço de lembretes
        lembrete_service.iniciar()
        
        # Inicia polling
        print("\n🔄 Bot rodando... (Ctrl+C para parar)")
        print("-" * 70)
        bot.infinity_polling(timeout=30, long_polling_timeout=25)
        
    except KeyboardInterrupt:
        print("\n👋 Bot interrompido pelo usuário")
        lembrete_service.parar()
        
    except Exception as e:
        logger.error(f"💀 ERRO FATAL: {e}", exc_info=True)
        print(f"\n💀 ERRO FATAL: {e}")


if __name__ == "__main__":
    main()