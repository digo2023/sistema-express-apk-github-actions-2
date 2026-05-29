from datetime import datetime, timedelta
from modulos.banco_dados import fetchall
from modulos.interface import header, warn, ok, tabela, pause
from modulos.utilitarios import iso_to_br, fmt_qtd
from configuracao import agora_br


def obter_alertas():
    out=[]
    baixos = fetchall('''SELECT p.codigo,p.nome,p.categoria,p.unidade,p.estoque_minimo,COALESCE(SUM(e.quantidade),0) AS total
                         FROM produtos p LEFT JOIN estoque_locais e ON e.produto_id=p.id
                         WHERE p.ativo=1 GROUP BY p.id HAVING p.estoque_minimo>0 AND total<=p.estoque_minimo ORDER BY p.nome''')
    for r in baixos:
        out.append(('ESTOQUE BAIXO', r['codigo'], r['nome'], f"{fmt_qtd(r['total'],r['unidade'])} {r['unidade']}", f"Mínimo: {fmt_qtd(r['estoque_minimo'],r['unidade'])}"))
    hoje = agora_br().date(); limite = hoje + timedelta(days=7)
    vals = fetchall('''SELECT p.codigo,p.nome,p.unidade,e.localizacao,e.validade,e.lote,e.quantidade FROM estoque_locais e
                       JOIN produtos p ON p.id=e.produto_id WHERE p.ativo=1 AND e.validade<>'' AND e.quantidade>0 ORDER BY e.validade ASC''')
    for r in vals:
        try: d = datetime.strptime(r['validade'], '%Y-%m-%d').date()
        except Exception: continue
        if d < hoje: out.append(('VENCIDO', r['codigo'], r['nome'], iso_to_br(r['validade']), f"{r['localizacao']} | {fmt_qtd(r['quantidade'],r['unidade'])} {r['unidade']} | Lote {r['lote']}"))
        elif d <= limite: out.append(('VENCE EM 7 DIAS', r['codigo'], r['nome'], iso_to_br(r['validade']), f"{r['localizacao']} | {fmt_qtd(r['quantidade'],r['unidade'])} {r['unidade']} | Lote {r['lote']}"))
    return out


def painel_alertas():
    header('ALERTAS')
    rows=obter_alertas()
    if rows:
        warn(f'{len(rows)} alerta(s) encontrados.')
        tabela('ALERTAS OPERACIONAIS', ['Tipo','Código','Produto','Situação','Detalhe'], rows, 200)
    else: ok('Nenhum alerta crítico encontrado.')
    pause()
