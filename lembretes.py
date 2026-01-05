"""
Módulo de sistema de lembretes
"""
import logging
import time
from datetime import datetime
from typing import Optional
from threading import Thread

from config import (
    LEMBRETE_24H, LEMBRETE_3H, LEMBRETE_30MIN,
    TOLERANCIA_24H, TOLERANCIA_3H, TOLERANCIA_30MIN,
    INTERVALO_VERIFICACAO
)
from database import Database
from utils import DateTimeUtils

logger = logging.getLogger(__name__)


class LembreteService:
    """Serviço de gerenciamento de lembretes"""
    
    def __init__(self, bot):
        self.bot = bot
        self.running = False
        self.thread = None
    
    def iniciar(self):
        """Inicia o serviço de lembretes em thread separada"""
        if self.running:
            logger.warning("Serviço de lembretes já está rodando")
            return
        
        self.running = True
        self.thread = Thread(target=self._executar_loop, daemon=True)
        self.thread.start()
        logger.info("⏰ Serviço de lembretes iniciado")
    
    def parar(self):
        """Para o serviço de lembretes"""
        self.running = False
        logger.info("⏰ Serviço de lembretes parado")
    
    def _executar_loop(self):
        """Loop principal de verificação de lembretes"""
        while self.running:
            try:
                self._verificar_lembretes()
            except Exception as e:
                logger.error(f"❌ Erro na verificação de lembretes: {e}", exc_info=True)
            
            time.sleep(INTERVALO_VERIFICACAO)
    
    def _verificar_lembretes(self):
        """Verifica e envia lembretes necessários"""
        agora = datetime.now()
        plantoes = Database.buscar_todos_plantoes_ativos()
        
        for plantao in plantoes:
            try:
                self._processar_plantao(plantao, agora)
            except Exception as e:
                logger.error(f"❌ Erro ao processar plantão {plantao['id']}: {e}")
    
    def _processar_plantao(self, plantao, agora: datetime):
        """Processa um plantão verificando lembretes"""
        plantao_id = plantao['id']
        chat_id = plantao['chat_id']
        data_str = plantao['data']
        hora_str = plantao['hora']
        local = plantao['local']
        
        # Parse da data/hora do plantão
        data_plantao = DateTimeUtils.parse_data_hora(data_str, hora_str)
        if not data_plantao:
            logger.warning(f"Data/hora inválida para plantão {plantao_id}")
            return
        
        # Se plantão já passou, pula
        if data_plantao < agora:
            return
        
        # Calcula horas restantes
        horas_restantes = (data_plantao - agora).total_seconds() / 3600
        
        # Verifica cada tipo de lembrete
        self._verificar_lembrete_24h(plantao, horas_restantes, chat_id, data_str, hora_str, local)
        self._verificar_lembrete_3h(plantao, horas_restantes, chat_id, data_str, hora_str, local)
        self._verificar_lembrete_30min(plantao, horas_restantes, chat_id, data_str, hora_str, local)
    
    def _verificar_lembrete_24h(self, plantao, horas_restantes, chat_id, data_str, hora_str, local):
        """Verifica e envia lembrete de 24 horas"""
        if plantao['lembrete_24h']:
            return
        
        limite_inferior = LEMBRETE_24H - TOLERANCIA_24H
        limite_superior = LEMBRETE_24H + TOLERANCIA_24H
        
        if limite_inferior <= horas_restantes <= limite_superior:
            mensagem = self._criar_mensagem_24h(data_str, hora_str, local)
            self._enviar_lembrete(chat_id, mensagem, plantao['id'], '24h')
    
    def _verificar_lembrete_3h(self, plantao, horas_restantes, chat_id, data_str, hora_str, local):
        """Verifica e envia lembrete de 3 horas"""
        if plantao['lembrete_3h']:
            return
        
        limite_inferior = LEMBRETE_3H - TOLERANCIA_3H
        limite_superior = LEMBRETE_3H + TOLERANCIA_3H
        
        if limite_inferior <= horas_restantes <= limite_superior:
            mensagem = self._criar_mensagem_3h(data_str, hora_str, local)
            self._enviar_lembrete(chat_id, mensagem, plantao['id'], '3h')
    
    def _verificar_lembrete_30min(self, plantao, horas_restantes, chat_id, data_str, hora_str, local):
        """Verifica e envia lembrete de 30 minutos"""
        if plantao['lembrete_30min']:
            return
        
        limite_inferior = LEMBRETE_30MIN - TOLERANCIA_30MIN
        limite_superior = LEMBRETE_30MIN + TOLERANCIA_30MIN
        
        if limite_inferior <= horas_restantes <= limite_superior:
            mensagem = self._criar_mensagem_30min(data_str, hora_str, local)
            self._enviar_lembrete(chat_id, mensagem, plantao['id'], '30min')
    
    def _enviar_lembrete(self, chat_id: int, mensagem: str, plantao_id: int, tipo: str):
        """Envia lembrete e atualiza banco de dados (com proteção contra duplicatas)"""
        try:
            # Primeiro atualiza o banco (marca como enviado)
            Database.atualizar_lembrete(plantao_id, tipo)
            
            # Depois envia a mensagem
            self.bot.send_message(chat_id, mensagem, parse_mode='Markdown')
            
            logger.info(f"✅ Lembrete {tipo} enviado para plantão {plantao_id}")
        except Exception as e:
            logger.error(f"❌ Erro ao enviar lembrete {tipo}: {e}")
            # Se der erro ao enviar, reverte a marcação
            # (comentado para não ficar tentando enviar infinitamente)
            # Database.reverter_lembrete(plantao_id, tipo)
    
    @staticmethod
    def _criar_mensagem_24h(data_str: str, hora_str: str, local: str) -> str:
        """Cria mensagem de lembrete 24h"""
        return f"""
⏰ *LEMBRETE 24H - PLANTÃO AMANHÃ!*

📅 {data_str} às {hora_str}
🏥 {local}

💡 *Checklist:*
• ✅ Estetoscópio
• ✅ Jaleco
• ✅ Lanche/água
• ✅ Carregador
• ✅ Roupas confortáveis
• ✅ Documentos

💪 Boa sorte, amore! ❤️
"""
    
    @staticmethod
    def _criar_mensagem_3h(data_str: str, hora_str: str, local: str) -> str:
        """Cria mensagem de lembrete 3h"""
        return f"""
🚨 *PLANTÃO EM 3 HORAS!*

🏥 {local}
⏰ {hora_str}

⚡ *Hora de se preparar!*
• Verifique o trânsito
• Separe tudo que precisa
• Alimente-se bem

❤️ Vai dar tudo certo!
"""
    
    @staticmethod
    def _criar_mensagem_30min(data_str: str, hora_str: str, local: str) -> str:
        """Cria mensagem de lembrete 30min"""
        return f"""
🚨🚨 *PLANTÃO EM 30 MINUTOS!*

🏥 {local}
⏰ {hora_str}

⚡⚡ *HORA DE SAIR!*
• Vá com segurança
• Você é incrível!

❤️❤️ BOA PLANTÃO, AMORE! ❤️❤️
"""


def enviar_notificacao_namorado(bot, chat_id_namorado: str, data_str: str, hora_str: str, local: str):
    """Envia notificação para o namorado quando plantão é adicionado"""
    if not chat_id_namorado:
        return
    
    mensagem = f"""
👩‍⚕️ *SUA NAMORADA ADICIONOU UM PLANTÃO!*

📅 {data_str} ⏰ {hora_str}
🏥 {local}

💌 *Mande uma mensagem carinhosa para ela!*
💪 *Deseje boa sorte!*
❤️ *Mostre que você se importa!*
"""
    
    try:
        bot.send_message(chat_id_namorado, mensagem, parse_mode='Markdown')
        logger.info(f"💌 Notificação enviada para namorado: {data_str} {hora_str}")
    except Exception as e:
        logger.error(f"❌ Erro ao notificar namorado: {e}")