from datetime import datetime
from configuracao import DATE_FMT, ISO_DATE_FMT, TURNOS, UNIDADES_INTEIRAS, agora_br
from modulos.banco_dados import fetchall, fetchone
from modulos.interface import ask, ask_float, warn, tabela, confirm

def br_to_iso(data):
    if not data:
        return ''
    data = str(data).strip()
    try:
        if '-' in data and len(data) == 10:
            return datetime.strptime(data, ISO_DATE_FMT).strftime(ISO_DATE_FMT)
        return datetime.strptime(data, DATE_FMT).strftime(ISO_DATE_FMT)
    except Exception:
        return ''

def iso_to_br(data):
    if not data: return ''
    try: return datetime.strptime(data[:10], ISO_DATE_FMT).strftime(DATE_FMT)
    except Exception: return data

def pedir_data(label, default_hoje=True, obrigatoria=True):
    default = agora_br().strftime(DATE_FMT) if default_hoje else None
    while True:
        raw = ask(label, default=default, required=obrigatoria)
        if not raw and not obrigatoria: return ''
        iso = br_to_iso(raw)
        if iso: return iso
        warn('Data inválida. Use DD/MM/AAAA.')

def pedir_turno():
    while True:
        t = ask('Turno [A=Almoço | B=Janta | C=Ceia]', upper=True, required=True)
        if t in TURNOS: return t
        warn('Turno inválido. Digite A, B ou C.')

def fmt_qtd(qtd, unidade=''):
    try: val = float(qtd)
    except Exception: return str(qtd)
    un = str(unidade or '').upper().strip()
    if un in UNIDADES_INTEIRAS and val.is_integer(): return str(int(val))
    if val.is_integer() and un not in {'KG','G','L','ML'}: return str(int(val))
    return f"{val:,.3f}".replace(',', 'X').replace('.', ',').replace('X','.')

def estoque_total(produto_id):
    r = fetchone('SELECT COALESCE(SUM(quantidade),0) AS q FROM estoque_locais WHERE produto_id=?', (produto_id,))
    return float(r['q'] if r else 0)

def buscar_produtos(termo):
    like = f"%{termo.upper().strip()}%"
    return fetchall('''SELECT p.*, COALESCE((SELECT SUM(e.quantidade) FROM estoque_locais e WHERE e.produto_id=p.id),0) AS total
                       FROM produtos p WHERE p.ativo=1 AND (UPPER(p.codigo) LIKE ? OR UPPER(p.nome) LIKE ? OR UPPER(COALESCE(p.codigo_barras,'')) LIKE ?) ORDER BY p.nome''', (like, like, like))

def selecionar_produto(oferecer_cadastro=False):
    from modulos.produtos import cadastrar_produto_fluxo
    while True:
        termo = ask('Digite código ou parte do nome do produto', required=True)
        rows = buscar_produtos(termo)
        if not rows:
            warn('Produto não encontrado.')
            if oferecer_cadastro and confirm('Deseja cadastrar este produto agora?', default=True):
                return cadastrar_produto_fluxo(nome_sugerido=termo)
            if ask('Digite 0 para voltar ou ENTER para pesquisar novamente', default='') == '0': return None
            continue
        if len(rows) == 1:
            return rows[0]
        dados = [(i+1, r['codigo'], r['nome'], r['categoria'], r['codigo_barras'] or '', fmt_qtd(r['total'], r['unidade']), r['unidade']) for i,r in enumerate(rows)]
        tabela('PRODUTOS ENCONTRADOS', ['Nº','Código','Produto','Categoria','Cód. Barras','Estoque','Un'], dados)
        op = ask('Escolha o número do produto ou 0 para pesquisar novamente', required=True)
        if op == '0': continue
        if op.isdigit() and 1 <= int(op) <= len(rows): return rows[int(op)-1]
        warn('Opção inválida.')

def locais_produto(produto_id):
    return fetchall('''SELECT * FROM estoque_locais WHERE produto_id=? ORDER BY localizacao, validade, lote''', (produto_id,))

def escolher_local(produto, somente_com_estoque=False):
    rows = locais_produto(produto['id'])
    if somente_com_estoque: rows = [r for r in rows if float(r['quantidade']) > 0]
    if not rows:
        return None
    if len(rows) == 1:
        return rows[0]
    dados = [(i+1, r['localizacao'], r['lote'], iso_to_br(r['validade']), fmt_qtd(r['quantidade'], produto['unidade'])) for i,r in enumerate(rows)]
    tabela('LOCALIZAÇÕES DO PRODUTO', ['Nº','Local','Lote','Validade','Qtd'], dados)
    while True:
        op = ask('Escolha o número da localização ou 0 para voltar', required=True)
        if op == '0':
            return None
        if op.isdigit() and 1 <= int(op) <= len(rows):
            return rows[int(op)-1]
        warn('Opção inválida.')

def resumo_produto(produto):
    total = estoque_total(produto['id'])
    return f"{produto['codigo']} | {produto['nome']} | Total: {fmt_qtd(total, produto['unidade'])} {produto['unidade']}"


def pedir_periodo(label_ini='Data inicial', label_fim='Data final'):
    """Pede período e impede data final menor que inicial."""
    while True:
        ini = pedir_data(label_ini)
        fim = pedir_data(label_fim)
        if ini <= fim:
            return ini, fim
        warn('Período inválido: a data final não pode ser menor que a data inicial.')

def nome_arquivo_seguro(nome, limite=120):
    """Limpa nomes vindos do usuário para salvar cópias/importações com segurança."""
    import re
    base = str(nome or 'arquivo').split('/')[-1].split('\\')[-1]
    base = re.sub(r'[^A-Za-z0-9_. -]+', '_', base).strip().strip('.')
    return (base or 'arquivo')[:limite]


def buscar_produto_por_barra(codigo_barra):
    cod = str(codigo_barra or '').strip()
    if not cod:
        return None
    return fetchone("""SELECT p.*, COALESCE((SELECT SUM(e.quantidade) FROM estoque_locais e WHERE e.produto_id=p.id),0) AS total
                       FROM produtos p WHERE p.ativo=1 AND (p.codigo_barras=? OR p.codigo=?) LIMIT 1""", (cod, cod))
