"""
Módulo de teclados personalizados do Telegram
"""
from telebot import types
from datetime import datetime, timedelta


class KeyboardFactory:
    """Factory para criar teclados personalizados"""
    
    @staticmethod
    def criar_teclado_principal():
        """Cria teclado principal do bot"""
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        
        botoes = [
            types.KeyboardButton("➕ Plantão"),
            types.KeyboardButton("📅 Hoje"),
            types.KeyboardButton("📆 Amanhã"),
            types.KeyboardButton("📋 Próximos"),
            types.KeyboardButton("🗑️ Deletar"),
            types.KeyboardButton("🔧 Debug"),
            types.KeyboardButton("❓ Ajuda")
        ]
        
        markup.row(botoes[0], botoes[1], botoes[2])
        markup.row(botoes[3], botoes[4])
        markup.row(botoes[5], botoes[6])
        
        return markup
    
    @staticmethod
    def criar_teclado_data_hora():
        """Cria teclado com sugestões de data/hora"""
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        
        hoje = datetime.now()
        amanha = hoje + timedelta(days=1)
        
        # Sugestões de data/hora comuns
        markup.row(
            types.KeyboardButton(f"{hoje.strftime('%d/%m')} 19:00"),
            types.KeyboardButton(f"{amanha.strftime('%d/%m')} 07:00")
        )
        markup.row(
            types.KeyboardButton(f"{hoje.strftime('%d/%m')} 07:00"),
            types.KeyboardButton(f"{amanha.strftime('%d/%m')} 19:00")
        )
        markup.row(types.KeyboardButton("❌ Cancelar"))
        
        return markup
    
    @staticmethod
    def criar_teclado_locais():
        """Cria teclado com sugestões de locais (Londrina e Cambé - PR)"""
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True, row_width=1)
        
        # Hospitais e UPAs de Londrina
        locais_londrina = [
            "🏥 Hospital Universitário (HU-UEL)",
            "🏥 Hospital Evangélico",
            "🏥 Hospital da Providência",
            "🏥 Hospital do Coração (HCor)",
            "🏥 Santa Casa de Londrina",
            "🏥 Mater Dei",
            "🚑 UPA Norte (Londrina)",
            "🚑 UPA Sul (Londrina)",
            "🚑 UPA Leste (Londrina)",
            "🚑 UPA Oeste (Londrina)",
        ]
        
        # Hospitais e UPAs de Cambé
        locais_cambe = [
            "🏥 Hospital e Maternidade de Cambé",
            "🚑 UPA Cambé",
            "🏥 Santa Casa de Cambé",
        ]
        
        # Adicionar todos os locais
        for local in locais_londrina:
            markup.row(types.KeyboardButton(local))
        
        for local in locais_cambe:
            markup.row(types.KeyboardButton(local))
        
        # Opção para outro local
        markup.row(types.KeyboardButton("📍 Outro local"))
        markup.row(types.KeyboardButton("❌ Cancelar"))
        
        return markup
    
    @staticmethod
    def criar_teclado_confirmacao():
        """Cria teclado de confirmação"""
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.row(
            types.KeyboardButton("✅ Confirmar"),
            types.KeyboardButton("❌ Cancelar")
        )
        return markup
    
    @staticmethod
    def criar_inline_compartilhar(plantao_id: int):
        """Cria botões inline para compartilhar plantão"""
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("📱 Compartilhar", 
                                      switch_inline_query=f"plantao_{plantao_id}"),
            types.InlineKeyboardButton("🗑️ Excluir", 
                                      callback_data=f"delete_{plantao_id}")
        )
        return markup