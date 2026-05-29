import sqlite3
from pathlib import Path
from configuracao import DB_PATH, DATA_DIR, agora_br

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS produtos(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 codigo TEXT UNIQUE NOT NULL,
 nome TEXT NOT NULL,
 categoria TEXT NOT NULL,
 unidade TEXT NOT NULL,
 estoque_minimo REAL NOT NULL DEFAULT 0,
 observacao TEXT DEFAULT '',
 codigo_barras TEXT DEFAULT '',
 ativo INTEGER NOT NULL DEFAULT 1,
 criado_em TEXT NOT NULL DEFAULT (datetime('now','localtime')),
 atualizado_em TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);
CREATE TABLE IF NOT EXISTS estoque_locais(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 produto_id INTEGER NOT NULL,
 localizacao TEXT NOT NULL DEFAULT 'GERAL',
 lote TEXT DEFAULT '',
 validade TEXT DEFAULT '',
 quantidade REAL NOT NULL DEFAULT 0,
 atualizado_em TEXT NOT NULL DEFAULT (datetime('now','localtime')),
 UNIQUE(produto_id, localizacao, lote, validade),
 FOREIGN KEY(produto_id) REFERENCES produtos(id)
);
CREATE TABLE IF NOT EXISTS movimentacoes(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 produto_id INTEGER NOT NULL,
 tipo TEXT NOT NULL,
 quantidade REAL NOT NULL,
 unidade TEXT NOT NULL,
 localizacao TEXT DEFAULT '',
 lote TEXT DEFAULT '',
 validade TEXT DEFAULT '',
 data_movimento TEXT NOT NULL,
 data_consumo TEXT DEFAULT '',
 turno TEXT DEFAULT '',
 motivo TEXT DEFAULT '',
 observacao TEXT DEFAULT '',
 estoque_antes REAL DEFAULT 0,
 estoque_depois REAL DEFAULT 0,
 criado_em TEXT NOT NULL DEFAULT (datetime('now','localtime')),
 FOREIGN KEY(produto_id) REFERENCES produtos(id)
);
CREATE TABLE IF NOT EXISTS conferencias(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 produto_id INTEGER NOT NULL,
 localizacao TEXT DEFAULT '',
 quantidade_sistema REAL NOT NULL,
 quantidade_fisica REAL NOT NULL,
 diferenca REAL NOT NULL,
 ajustado INTEGER NOT NULL DEFAULT 0,
 data_conferencia TEXT NOT NULL,
 observacao TEXT DEFAULT '',
 criado_em TEXT NOT NULL DEFAULT (datetime('now','localtime')),
 FOREIGN KEY(produto_id) REFERENCES produtos(id)
);
CREATE TABLE IF NOT EXISTS eventos(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 tipo TEXT NOT NULL,
 descricao TEXT NOT NULL,
 criado_em TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);
CREATE TABLE IF NOT EXISTS oc_itens(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 documento TEXT DEFAULT '',
 data_entrega TEXT DEFAULT '',
 data_utilizacao TEXT DEFAULT '',
 codigo TEXT DEFAULT '',
 item TEXT NOT NULL,
 quantidade REAL NOT NULL DEFAULT 0,
 unidade TEXT DEFAULT '',
 observacao TEXT DEFAULT '',
 emissao TEXT DEFAULT '',
 versao TEXT DEFAULT '',
 filial_codigo TEXT DEFAULT '',
 filial_nome TEXT DEFAULT '',
 periodo_entrega_inicio TEXT DEFAULT '',
 periodo_entrega_fim TEXT DEFAULT '',
 solicitacao TEXT DEFAULT '',
 sequencia TEXT DEFAULT '',
 data_solicitacao TEXT DEFAULT '',
 descricao TEXT DEFAULT '',
 criado_em TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);
CREATE TABLE IF NOT EXISTS ajustes_manuais(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 modulo TEXT NOT NULL,
 descricao TEXT NOT NULL,
 usuario TEXT DEFAULT '',
 criado_em TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);
CREATE TABLE IF NOT EXISTS analitico_itens(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 arquivo TEXT DEFAULT '',
 data TEXT DEFAULT '',
 servico TEXT DEFAULT '',
 turno TEXT DEFAULT '',
 codigo TEXT DEFAULT '',
 item TEXT NOT NULL,
 quantidade REAL NOT NULL,
 unidade TEXT DEFAULT '',
 categoria TEXT DEFAULT '',
 emissao TEXT DEFAULT '',
 versao TEXT DEFAULT '',
 filial_codigo TEXT DEFAULT '',
 filial_nome TEXT DEFAULT '',
 dia_semana TEXT DEFAULT '',
 codigo_servico TEXT DEFAULT '',
 refeicoes_estimadas REAL DEFAULT 0,
 limite_entrega TEXT DEFAULT '',
 codigo_prato TEXT DEFAULT '',
 nome_prato TEXT DEFAULT '',
 comensais_prato REAL DEFAULT 0,
 consumo_percentual REAL DEFAULT 0,
 per_capita REAL DEFAULT 0,
 criado_em TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);
"""

INDICES = [
    'CREATE INDEX IF NOT EXISTS idx_produtos_nome ON produtos(nome)',
    'CREATE INDEX IF NOT EXISTS idx_produtos_codigo ON produtos(codigo)',
    'CREATE INDEX IF NOT EXISTS idx_produtos_barras ON produtos(codigo_barras)',
    'CREATE INDEX IF NOT EXISTS idx_produtos_ativo ON produtos(ativo)',
    'CREATE INDEX IF NOT EXISTS idx_estoque_produto ON estoque_locais(produto_id)',
    'CREATE INDEX IF NOT EXISTS idx_estoque_local ON estoque_locais(localizacao)',
    'CREATE INDEX IF NOT EXISTS idx_mov_produto_data ON movimentacoes(produto_id, data_movimento)',
    'CREATE INDEX IF NOT EXISTS idx_mov_tipo_data ON movimentacoes(tipo, data_movimento)',
    'CREATE INDEX IF NOT EXISTS idx_analitico_data_turno ON analitico_itens(data, turno)',
    'CREATE INDEX IF NOT EXISTS idx_analitico_codigo ON analitico_itens(codigo)',
    'CREATE INDEX IF NOT EXISTS idx_analitico_item ON analitico_itens(item)',
    'CREATE INDEX IF NOT EXISTS idx_oc_item ON oc_itens(item)',
    'CREATE INDEX IF NOT EXISTS idx_oc_codigo ON oc_itens(codigo)',
    'CREATE INDEX IF NOT EXISTS idx_oc_utilizacao ON oc_itens(data_utilizacao)',
]

COLUNAS_ESPERADAS = {
    'produtos': {
        'estoque_minimo': 'REAL NOT NULL DEFAULT 0',
        'observacao': "TEXT DEFAULT ''",
        'codigo_barras': "TEXT DEFAULT ''",
        'ativo': 'INTEGER NOT NULL DEFAULT 1',
        'criado_em': "TEXT DEFAULT ''",
        'atualizado_em': "TEXT DEFAULT ''",
    },
    'estoque_locais': {
        'localizacao': "TEXT NOT NULL DEFAULT 'GERAL'",
        'lote': "TEXT DEFAULT ''",
        'validade': "TEXT DEFAULT ''",
        'quantidade': 'REAL NOT NULL DEFAULT 0',
        'atualizado_em': "TEXT DEFAULT ''",
    },
    'movimentacoes': {
        'localizacao': "TEXT DEFAULT ''", 'lote': "TEXT DEFAULT ''", 'validade': "TEXT DEFAULT ''",
        'data_consumo': "TEXT DEFAULT ''", 'turno': "TEXT DEFAULT ''", 'motivo': "TEXT DEFAULT ''",
        'observacao': "TEXT DEFAULT ''", 'estoque_antes': 'REAL DEFAULT 0', 'estoque_depois': 'REAL DEFAULT 0',
        'criado_em': "TEXT DEFAULT ''",
    },
    'conferencias': {
        'localizacao': "TEXT DEFAULT ''", 'ajustado': 'INTEGER NOT NULL DEFAULT 0',
        'observacao': "TEXT DEFAULT ''", 'criado_em': "TEXT DEFAULT ''",
    },
    'analitico_itens': {
        'arquivo': "TEXT DEFAULT ''", 'data': "TEXT DEFAULT ''", 'servico': "TEXT DEFAULT ''", 'turno': "TEXT DEFAULT ''",
        'codigo': "TEXT DEFAULT ''", 'unidade': "TEXT DEFAULT ''", 'categoria': "TEXT DEFAULT ''",
        'emissao': "TEXT DEFAULT ''", 'versao': "TEXT DEFAULT ''", 'filial_codigo': "TEXT DEFAULT ''",
        'filial_nome': "TEXT DEFAULT ''", 'dia_semana': "TEXT DEFAULT ''", 'codigo_servico': "TEXT DEFAULT ''",
        'refeicoes_estimadas': 'REAL DEFAULT 0', 'limite_entrega': "TEXT DEFAULT ''",
        'codigo_prato': "TEXT DEFAULT ''", 'nome_prato': "TEXT DEFAULT ''", 'comensais_prato': 'REAL DEFAULT 0',
        'consumo_percentual': 'REAL DEFAULT 0', 'per_capita': 'REAL DEFAULT 0',
        'criado_em': "TEXT DEFAULT ''",
    },
    'oc_itens': {
        'documento': "TEXT DEFAULT ''", 'data_entrega': "TEXT DEFAULT ''", 'data_utilizacao': "TEXT DEFAULT ''",
        'codigo': "TEXT DEFAULT ''", 'unidade': "TEXT DEFAULT ''", 'observacao': "TEXT DEFAULT ''",
        'emissao': "TEXT DEFAULT ''", 'versao': "TEXT DEFAULT ''", 'filial_codigo': "TEXT DEFAULT ''",
        'filial_nome': "TEXT DEFAULT ''", 'periodo_entrega_inicio': "TEXT DEFAULT ''", 'periodo_entrega_fim': "TEXT DEFAULT ''",
        'solicitacao': "TEXT DEFAULT ''", 'sequencia': "TEXT DEFAULT ''", 'data_solicitacao': "TEXT DEFAULT ''",
        'descricao': "TEXT DEFAULT ''", 'criado_em': "TEXT DEFAULT ''",
    },
}

TABELAS_VALIDAS = set(COLUNAS_ESPERADAS)


def connect():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys=ON')
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA synchronous=NORMAL')
    conn.execute('PRAGMA busy_timeout=5000')
    return conn


def _table_exists(conn, table):
    if table not in TABELAS_VALIDAS and table not in {'eventos', 'ajustes_manuais'}:
        return False
    row = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone()
    return row is not None


def _colunas(conn, table):
    return {r[1] for r in conn.execute(f'PRAGMA table_info({table})').fetchall()}


def _add_column_if_missing(conn, table, column, ddl):
    if table not in TABELAS_VALIDAS:
        raise RuntimeError(f'Tabela inválida para migração: {table}')
    if not _table_exists(conn, table):
        return
    cols = _colunas(conn, table)
    if column not in cols:
        conn.execute(f'ALTER TABLE {table} ADD COLUMN {column} {ddl}')


def migrate_db(conn):
    """Migração segura e cumulativa.

    Não apaga tabelas, não recria dados e não reduz histórico. Serve para abrir bancos antigos,
    bancos restaurados de backup e bancos já atualizados. Índices só são criados depois de
    garantir que as colunas existem, evitando falhas como "no such column: codigo_barras".
    """
    conn.execute('BEGIN')
    try:
        for tabela, colunas in COLUNAS_ESPERADAS.items():
            for coluna, ddl in colunas.items():
                _add_column_if_missing(conn, tabela, coluna, ddl)
        # Normalizações não destrutivas para bancos antigos.
        if _table_exists(conn, 'produtos'):
            conn.execute("UPDATE produtos SET codigo_barras='' WHERE codigo_barras IS NULL")
            conn.execute("UPDATE produtos SET observacao='' WHERE observacao IS NULL")
            conn.execute("UPDATE produtos SET ativo=1 WHERE ativo IS NULL")
            conn.execute("UPDATE produtos SET criado_em=datetime('now','localtime') WHERE criado_em IS NULL OR criado_em=''")
            conn.execute("UPDATE produtos SET atualizado_em=datetime('now','localtime') WHERE atualizado_em IS NULL OR atualizado_em=''")
        for indice in INDICES:
            conn.execute(indice)
        conn.execute('PRAGMA user_version=4332')
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def init_db():
    with connect() as conn:
        conn.executescript(SCHEMA)
        migrate_db(conn)


def execute(sql, params=()):
    with connect() as conn:
        cur = conn.execute(sql, params)
        conn.commit()
        return cur.lastrowid


def executemany(sql, seq_params):
    with connect() as conn:
        cur = conn.executemany(sql, seq_params)
        conn.commit()
        return cur.rowcount


def fetchall(sql, params=()):
    with connect() as conn:
        return conn.execute(sql, params).fetchall()


def fetchone(sql, params=()):
    with connect() as conn:
        return conn.execute(sql, params).fetchone()


def evento(tipo, descricao):
    execute('INSERT INTO eventos(tipo,descricao,criado_em) VALUES(?,?,?)', (tipo, descricao, agora_br().strftime('%Y-%m-%d %H:%M:%S')))
