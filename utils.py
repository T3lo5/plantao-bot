"""
Módulo de utilidades e funções auxiliares
"""
from datetime import datetime, timedelta
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class DateTimeUtils:
    """Utilitários para manipulação de data/hora"""
    
    @staticmethod
    def validar_data(data_str: str) -> bool:
        """Valida formato de data DD/MM"""
        try:
            dia, mes = data_str.split('/')
            dia, mes = int(dia), int(mes)
            return 1 <= dia <= 31 and 1 <= mes <= 12
        except:
            return False
    
    @staticmethod
    def validar_hora(hora_str: str) -> bool:
        """Valida formato de hora HH:MM"""
        try:
            hora, minuto = hora_str.split(':')
            hora, minuto = int(hora), int(minuto)
            return 0 <= hora <= 23 and 0 <= minuto <= 59
        except:
            return False
    
    @staticmethod
    def parse_data_hora(data_str: str, hora_str: str) -> Optional[datetime]:
        """Converte strings de data/hora para datetime com lógica inteligente de ano"""
        try:
            dia, mes = data_str.split('/')
            hora, minuto = hora_str.split(':')
            agora = datetime.now()
            ano_atual = agora.year
            
            # Tentar com ano atual primeiro
            data_plantao = datetime(
                ano_atual, 
                int(mes), 
                int(dia), 
                int(hora), 
                int(minuto)
            )
            
            # Lógica inteligente para determinar o ano:
            # Se a data já passou há MAIS de 6 meses, provavelmente é ano que vem
            # Se passou há menos de 6 meses, provavelmente é uma data passada mesmo
            diferenca = (agora - data_plantao).days
            
            if diferenca > 180:  # Mais de 6 meses no passado
                # Provavelmente é ano que vem
                data_plantao = data_plantao.replace(year=ano_atual + 1)
            elif diferenca > 0:  # Passou há menos de 6 meses
                # É uma data passada mesmo, manter ano atual
                pass
            # Se diferenca <= 0, é data futura no ano atual, manter como está
            
            return data_plantao
        except Exception as e:
            logger.error(f"Erro ao fazer parse de data/hora: {e}")
            return None
    
    @staticmethod
    def calcular_tempo_restante(data_plantao: datetime) -> Tuple[float, str]:
        """Calcula tempo restante até o plantão"""
        agora = datetime.now()
        diferenca = (data_plantao - agora).total_seconds() / 3600
        
        if diferenca < 0:
            return diferenca, "✅ JÁ PASSOU"
        elif diferenca < 0.5:
            minutos = int(diferenca * 60)
            return diferenca, f"🚨 EM {minutos} MIN"
        elif diferenca < 24:
            horas = int(diferenca)
            return diferenca, f"⏰ EM {horas} HORAS"
        else:
            dias = int(diferenca / 24)
            return diferenca, f"📅 EM {dias} DIAS"
    
    @staticmethod
    def obter_data_amanha() -> str:
        """Retorna data de amanhã no formato DD/MM"""
        amanha = datetime.now() + timedelta(days=1)
        return amanha.strftime("%d/%m")
    
    @staticmethod
    def obter_data_hoje() -> str:
        """Retorna data de hoje no formato DD/MM"""
        return datetime.now().strftime("%d/%m")


class MessageFormatter:
    """Formatador de mensagens do bot"""
    
    @staticmethod
    def formatar_plantao(data: str, hora: str, local: str) -> str:
        """Formata informações de um plantão"""
        return f"📅 *{data}* ⏰ *{hora}*\n🏥 {local}"
    
    @staticmethod
    def formatar_lista_plantoes(plantoes: list, titulo: str) -> str:
        """Formata uma lista de plantões"""
        if not plantoes:
            return "📭 Nenhum plantão encontrado."
        
        mensagem = f"{titulo}\n\n"
        for data, hora, local in plantoes:
            mensagem += f"{MessageFormatter.formatar_plantao(data, hora, local)}\n\n"
        
        return mensagem.strip()
    
    @staticmethod
    def formatar_checklist() -> str:
        """Retorna checklist para plantão"""
        return """
💡 *Checklist:*
• ✅ Estetoscópio
• ✅ Jaleco
• ✅ Lanche/água
• ✅ Carregador
• ✅ Roupas confortáveis
• ✅ Documentos
"""


class TelegramUtils:
    """Utilitários para Telegram"""
    
    @staticmethod
    def escapar_markdown(texto: str) -> str:
        """Escapa caracteres especiais do Markdown"""
        caracteres_especiais = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in caracteres_especiais:
            texto = texto.replace(char, f'\\{char}')
        return texto
    
    @staticmethod
    def truncar_mensagem(mensagem: str, tamanho_max: int = 4096) -> str:
        """Trunca mensagem para tamanho máximo do Telegram"""
        if len(mensagem) <= tamanho_max:
            return mensagem
        return mensagem[:tamanho_max-3] + "..."


def validar_formato_plantao(partes: list) -> Tuple[bool, str]:
    """Valida formato completo de um comando de plantão"""
    if len(partes) < 4:
        return False, "❌ Formato incompleto. Use: `/plantao DD/MM HH:MM Hospital`"
    
    data_str = partes[1]
    hora_str = partes[2]
    
    if not DateTimeUtils.validar_data(data_str):
        return False, "❌ Data inválida. Use formato DD/MM (ex: 15/03)"
    
    if not DateTimeUtils.validar_hora(hora_str):
        return False, "❌ Hora inválida. Use formato HH:MM (ex: 19:00)"
    
    return True, "OK"