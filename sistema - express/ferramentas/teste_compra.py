import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from modulos.banco_dados import init_db, execute, fetchall
from modulos.movimentacoes import upsert_local
from modulos.utilitarios import fmt_qtd

init_db()
try:
    pid = execute("INSERT INTO produtos(codigo,nome,categoria,unidade,estoque_minimo) VALUES(?,?,?,?,?)", ('TESTE_COMPRA', 'ARROZ TESTE COMPRA', 'NAO PERECIVEL', 'PACOTE', 10))
except Exception:
    pid = fetchall("SELECT id FROM produtos WHERE codigo='TESTE_COMPRA'")[0]['id']
upsert_local(pid, 'PRATELEIRA TESTE', '', '', 41)
assert fmt_qtd(41.0, 'PACOTE') == '41'
assert fetchall("SELECT COUNT(*) c FROM produtos")[0]['c'] >= 1
print('TESTE DE COMPRA OK')
