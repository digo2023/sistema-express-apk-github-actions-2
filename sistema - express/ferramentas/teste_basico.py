import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from modulos.banco_dados import init_db, execute, fetchone
from modulos.movimentacoes import upsert_local
from modulos.utilitarios import estoque_total, fmt_qtd
init_db()
code='TESTE_AUTO_V2'
row=fetchone('SELECT id FROM produtos WHERE codigo=?',(code,))
if not row:
    pid=execute('INSERT INTO produtos(codigo,nome,categoria,unidade,estoque_minimo,observacao) VALUES(?,?,?,?,?,?)',(code,'PRODUTO TESTE V2','NAO PERECIVEL','PACOTE',5,'teste'))
else:
    pid=row['id']
upsert_local(pid,'PRATELEIRA TESTE','','',41)
assert estoque_total(pid) >= 41
assert fmt_qtd(41.0,'PACOTE') == '41'
print('TESTE OK - banco, estoque por localização e formatação funcionando.')
