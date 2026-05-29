from pathlib import Path
from datetime import datetime, timezone, timedelta
try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None
import os
import time

APP_NAME = "SISTEMA EXCLUSIVO"
APP_COMPANY = "EXPRESS RESTAURANTES"
APP_UNIT = "UNIDADE COLORADO"
APP_SUBTITLE = "Gestão Operacional de Estoque, Produção, Compra e Conferência"
AUTHOR = "By Maicon"
TIMEZONE = "America/Sao_Paulo"  # Horário oficial de Brasília
try:
    os.environ["TZ"] = TIMEZONE
    if hasattr(time, "tzset"):
        time.tzset()
except Exception:
    pass
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
BACKUP_DIR = BASE_DIR / "backups"
REPORTS_DIR = BASE_DIR / "relatorios"
PDF_DIR = REPORTS_DIR / "pdf"
EXCEL_DIR = REPORTS_DIR / "excel"
ASSETS_DIR = BASE_DIR / "recursos"
IMPORT_DIR = BASE_DIR / "importados"
PASTA_IMPORTAR = BASE_DIR / "importar"
PASTA_ANALITICOS = PASTA_IMPORTAR / "analiticos"
PASTA_ORDENS_COMPRA = PASTA_IMPORTAR / "ordens_compra"
PASTA_BACKUPS_IMPORTAR = PASTA_IMPORTAR / "backups"
PASTA_OUTROS_IMPORTAR = PASTA_IMPORTAR / "outros"
# Mantido para recuperar backups gerados nas edições anteriores.
DB_PATH = DATA_DIR / "express_operacional.db"
DATE_FMT = "%d/%m/%Y"
ISO_DATE_FMT = "%Y-%m-%d"
CATEGORIAS = ["CONGELADO", "RESFRIADO", "NAO PERECIVEL", "HORTIFRUTI", "LIMPEZA", "DESCARTAVEL", "PROTEINAS", "OUTROS"]
UNIDADES = ["KG", "G", "UN", "PACOTE", "PCT", "CAIXA", "CX", "FARDO", "SACO", "L", "ML"]
UNIDADES_INTEIRAS = {"UN", "UNIDADE", "PACOTE", "PCT", "CAIXA", "CX", "FARDO", "SACO", "BDJ", "BANDEJA"}
TURNOS = {"A": "ALMOCO", "B": "JANTA", "C": "CEIA"}
TIPOS_OCORRENCIA = ["PERDA", "SOBRA", "DESPERDICIO", "AVARIA", "VENCIMENTO", "AJUSTE"]
for p in [DATA_DIR, BACKUP_DIR, PDF_DIR, EXCEL_DIR, ASSETS_DIR, IMPORT_DIR, PASTA_IMPORTAR, PASTA_ANALITICOS, PASTA_ORDENS_COMPRA, PASTA_BACKUPS_IMPORTAR, PASTA_OUTROS_IMPORTAR]:
    p.mkdir(parents=True, exist_ok=True)

def fuso_brasilia():
    """Retorna o fuso de Brasília com fallback seguro para Termux/Android.

    Em alguns aparelhos o banco de fusos IANA não vem instalado e o Python gera:
    No time zone found with key America/Sao_Paulo.
    Como o Brasil não usa horário de verão atualmente, UTC-03:00 mantém o horário de Brasília.
    """
    if ZoneInfo is not None:
        try:
            return ZoneInfo(TIMEZONE)
        except Exception:
            pass
    return timezone(timedelta(hours=-3), name="BRT")

def agora_br() -> datetime:
    """Data/hora oficial do sistema no horário de Brasília."""
    return datetime.now(fuso_brasilia())

def hoje_br() -> str:
    return agora_br().strftime(DATE_FMT)

def hora_br() -> str:
    return agora_br().strftime("%H:%M")

def data_hora_br() -> str:
    return agora_br().strftime("%d/%m/%Y - %H:%M")

def assinatura_relatorio() -> str:
    # Padrão obrigatório em todos os relatórios
    return f"{data_hora_br()} -By Maicon"

def agora_stamp() -> str:
    return agora_br().strftime("%Y%m%d_%H%M%S")
