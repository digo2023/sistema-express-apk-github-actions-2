#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from modulos.banco_dados import init_db, execute
from modulos.analitico import _buscar_consolidado, _buscar_detalhe_proteinas

init_db()
execute("DELETE FROM analitico_itens WHERE arquivo='TESTE_PLANEJAMENTO'")
execute("INSERT INTO analitico_itens(arquivo,data,servico,turno,codigo,item,quantidade,unidade,categoria) VALUES(?,?,?,?,?,?,?,?,?)", ('TESTE_PLANEJAMENTO','2026-05-07','ALMOCO','A','1.01.01.01.01','COXA SOBRECOXA',10.5,'KG','PROTEINAS'))
execute("INSERT INTO analitico_itens(arquivo,data,servico,turno,codigo,item,quantidade,unidade,categoria) VALUES(?,?,?,?,?,?,?,?,?)", ('TESTE_PLANEJAMENTO','2026-05-08','JANTAR','B','1.01.01.01.01','COXA SOBRECOXA',5.0,'KG','PROTEINAS'))
rows = _buscar_consolidado('2026-05-07','2026-05-08',['A','B','C'])
assert rows, 'sem consolidado'
assert float(rows[0]['qtd']) == 15.5
prot = _buscar_detalhe_proteinas('2026-05-07','2026-05-08',['A','B','C'])
assert len(prot) >= 2
print('Teste de planejamento concluído com sucesso.')
