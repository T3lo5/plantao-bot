"""
Módulo de gerenciamento do banco de dados
"""
import sqlite3
import logging
from datetime import datetime
from typing import List, Optional, Tuple
from contextlib import contextmanager
from config import DATABASE_NAME

logger = logging.getLogger(__name__)


@contextmanager
def get_db_connection():
    """Context manager para conexões do banco de dados"""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Erro no banco de dados: {e}")
        raise
    finally:
        conn.close()


class Database:
    """Classe para gerenciar operações do banco de dados"""
    
    @staticmethod
    def init_db():
        """Inicializa e verifica estrutura do banco de dados"""
        with get_db_connection() as conn:
            c = conn.cursor()
            
            # Criar tabela principal
            c.execute('''
                CREATE TABLE IF NOT EXISTS plantoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    data TEXT NOT NULL,
                    hora TEXT NOT NULL,
                    local TEXT NOT NULL,
                    lembrete_24h BOOLEAN DEFAULT 0,
                    lembrete_3h BOOLEAN DEFAULT 0,
                    lembrete_30min BOOLEAN DEFAULT 0,
                    ativo BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Criar índices para melhor performance
            c.execute('''
                CREATE INDEX IF NOT EXISTS idx_chat_id 
                ON plantoes(chat_id)
            ''')
            
            c.execute('''
                CREATE INDEX IF NOT EXISTS idx_data_hora 
                ON plantoes(data, hora)
            ''')
            
            # Verificar e adicionar colunas faltantes
            c.execute("PRAGMA table_info(plantoes)")
            colunas_existentes = [col[1] for col in c.fetchall()]
            
            colunas_necessarias = {
                'lembrete_24h': 'BOOLEAN DEFAULT 0',
                'lembrete_3h': 'BOOLEAN DEFAULT 0',
                'lembrete_30min': 'BOOLEAN DEFAULT 0',
                'ativo': 'BOOLEAN DEFAULT 1'
            }
            
            for coluna, tipo in colunas_necessarias.items():
                if coluna not in colunas_existentes:
                    try:
                        c.execute(f"ALTER TABLE plantoes ADD COLUMN {coluna} {tipo}")
                        logger.info(f"✅ Coluna {coluna} adicionada")
                    except sqlite3.OperationalError as e:
                        logger.warning(f"Coluna {coluna} já existe: {e}")
            
            conn.commit()
            logger.info("✅ Banco de dados inicializado com sucesso")
    
    @staticmethod
    def salvar_plantao(chat_id: int, data_str: str, hora_str: str, local: str) -> int:
        """Salva um novo plantão"""
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO plantoes (chat_id, data, hora, local) 
                VALUES (?, ?, ?, ?)
            ''', (chat_id, data_str, hora_str, local))
            plantao_id = c.lastrowid
            logger.info(f"📝 Plantão {plantao_id} salvo: {data_str} {hora_str} - {local}")
            return plantao_id
    
    @staticmethod
    def buscar_plantoes_por_data(chat_id: int, data_str: str) -> List[Tuple]:
        """Busca plantões de uma data específica"""
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('''
                SELECT data, hora, local 
                FROM plantoes 
                WHERE chat_id = ? AND data = ? AND ativo = 1
                ORDER BY hora
            ''', (chat_id, data_str))
            return c.fetchall()
    
    @staticmethod
    def buscar_proximos_plantoes(chat_id: int, limite: int = 5) -> List[Tuple]:
        """Busca os próximos plantões"""
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('''
                SELECT data, hora, local 
                FROM plantoes 
                WHERE chat_id = ? AND ativo = 1
                ORDER BY 
                    substr(data, 4, 2) || substr(data, 1, 2),
                    hora
                LIMIT ?
            ''', (chat_id, limite))
            return c.fetchall()
    
    @staticmethod
    def buscar_todos_plantoes_ativos() -> List[Tuple]:
        """Busca todos os plantões ativos para verificação de lembretes"""
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('''
                SELECT 
                    id, chat_id, data, hora, local,
                    COALESCE(lembrete_24h, 0) as lembrete_24h,
                    COALESCE(lembrete_3h, 0) as lembrete_3h,
                    COALESCE(lembrete_30min, 0) as lembrete_30min
                FROM plantoes 
                WHERE ativo = 1
            ''')
            return c.fetchall()
    
    @staticmethod
    def atualizar_lembrete(plantao_id: int, tipo_lembrete: str):
        """Atualiza o status de um lembrete"""
        campo = f"lembrete_{tipo_lembrete}"
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute(f'''
                UPDATE plantoes 
                SET {campo} = 1
                WHERE id = ?
            ''', (plantao_id,))
            logger.info(f"✅ Lembrete {tipo_lembrete} atualizado para plantão {plantao_id}")
    
    @staticmethod
    def desativar_plantao(plantao_id: int):
        """Desativa um plantão (soft delete)"""
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('''
                UPDATE plantoes 
                SET ativo = 0
                WHERE id = ?
            ''', (plantao_id,))
            logger.info(f"🗑️ Plantão {plantao_id} desativado")
    
    @staticmethod
    def contar_plantoes(chat_id: Optional[int] = None) -> int:
        """Conta plantões totais ou de um usuário específico"""
        with get_db_connection() as conn:
            c = conn.cursor()
            if chat_id:
                c.execute('SELECT COUNT(*) FROM plantoes WHERE chat_id = ? AND ativo = 1', (chat_id,))
            else:
                c.execute('SELECT COUNT(*) FROM plantoes WHERE ativo = 1')
            return c.fetchone()[0]
    
    @staticmethod
    def limpar_plantoes_antigos(dias: int = 30):
        """Remove plantões muito antigos do banco"""
        # Implementação futura para manutenção
        pass