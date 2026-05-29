from modulos.banco_dados import execute, fetchone, fetchall, evento
from modulos.interface import header, ask, ask_float, confirm, ok, warn, tabela, pause, menu
from modulos.utilitarios import selecionar_produto, pedir_data, pedir_turno, fmt_qtd, estoque_total, escolher_local, iso_to_br
from configuracao import TIPOS_OCORRENCIA


def upsert_local(produto_id, localizacao, lote, validade, delta):
    localizacao = (localizacao or 'GERAL').upper().strip()
    lote = (lote or '').upper().strip(); validade = validade or ''
    row = fetchone('SELECT * FROM estoque_locais WHERE produto_id=? AND localizacao=? AND lote=? AND validade=?', (produto_id, localizacao, lote, validade))
    if row:
        nova = float(row['quantidade']) + float(delta)
        if nova < -0.000001:
            raise ValueError('Movimentação bloqueada: o estoque da localização ficaria negativo.')
        if abs(nova) < 0.000001:
            nova = 0.0
        execute('UPDATE estoque_locais SET quantidade=?, atualizado_em=CURRENT_TIMESTAMP WHERE id=?', (nova, row['id']))
        return nova
    else:
        inicial = float(delta)
        if inicial < -0.000001:
            raise ValueError('Movimentação bloqueada: localização inexistente para baixa.')
        execute('INSERT INTO estoque_locais(produto_id,localizacao,lote,validade,quantidade) VALUES(?,?,?,?,?)', (produto_id, localizacao, lote, validade, inicial))
        return inicial


def entrada_estoque(rapida=False):
    header('ENTRADA RÁPIDA' if rapida else 'ENTRADA DE ESTOQUE')
    p = selecionar_produto(oferecer_cadastro=True)
    if not p: pause(); return
    print('\n' + f'Produto selecionado: {p["codigo"]} | {p["nome"]} | Unidade: {p["unidade"]}')
    qtd = ask_float('Quantidade recebida', min_value=0.000001)
    local = ask('Localização / prateleira', default='GERAL', upper=True, required=True)
    lote = '' if rapida else ask('Lote', default='', upper=True)
    validade = '' if rapida else pedir_data('Validade (ENTER para deixar vazio)', default_hoje=False, obrigatoria=False)
    data_mov = pedir_data('Data da entrada')
    motivo = 'ENTRADA RAPIDA' if rapida else ask('Motivo/Fornecedor/NF', default='ENTRADA', upper=True)
    obs = ask('Observação', default='')
    antes = estoque_total(p['id'])
    print('\nCONFIRMAÇÃO DA ENTRADA')
    print(f'Produto: {p["nome"]}\nQuantidade: {fmt_qtd(qtd,p["unidade"])} {p["unidade"]}\nLocal: {local}\nLote: {lote}\nValidade: {iso_to_br(validade)}\nData: {iso_to_br(data_mov)}\nObs: {obs}')
    if not confirm('Confirmar entrada?', default=True):
        warn('Entrada cancelada. Nada foi salvo.'); pause(); return
    upsert_local(p['id'], local, lote, validade, qtd)
    depois = estoque_total(p['id'])
    execute('''INSERT INTO movimentacoes(produto_id,tipo,quantidade,unidade,localizacao,lote,validade,data_movimento,motivo,observacao,estoque_antes,estoque_depois)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''', (p['id'],'ENTRADA',qtd,p['unidade'],local,lote,validade,data_mov,motivo,obs,antes,depois))
    evento('ENTRADA', f'{p["nome"]}: +{fmt_qtd(qtd,p["unidade"])} {p["unidade"]} em {local}')
    ok(f'Entrada salva. Estoque atual: {fmt_qtd(depois,p["unidade"])} {p["unidade"]}')
    pause()


def baixar_de_local(produto, qtd, local_row):
    if not local_row or float(local_row['quantidade']) < qtd:
        return False
    nova = float(local_row['quantidade']) - float(qtd)
    execute('UPDATE estoque_locais SET quantidade=?, atualizado_em=CURRENT_TIMESTAMP WHERE id=?', (nova, local_row['id']))
    return True


def saida_estoque(rapida=False):
    header('SAÍDA RÁPIDA' if rapida else 'SAÍDA DE ESTOQUE')
    p = selecionar_produto()
    if not p: pause(); return
    total = estoque_total(p['id'])
    print(f"\nProduto: {p['nome']} | Disponível total: {fmt_qtd(total,p['unidade'])} {p['unidade']}")
    if total <= 0:
        warn('Produto sem estoque disponível.'); pause(); return
    qtd = ask_float('Quantidade para saída', min_value=0.000001)
    if qtd > total:
        warn(f'Saída bloqueada. Disponível: {fmt_qtd(total,p["unidade"])} {p["unidade"]}.'); pause(); return
    loc = escolher_local(p, somente_com_estoque=True)
    if not loc: warn('Nenhuma localização com estoque.'); pause(); return
    if qtd > float(loc['quantidade']):
        warn(f'Local selecionado possui apenas {fmt_qtd(loc["quantidade"],p["unidade"])} {p["unidade"]}.'); pause(); return
    data_consumo = pedir_data('Data de consumo')
    turno = pedir_turno()
    motivo = 'SAIDA RAPIDA' if rapida else ask('Motivo', default='CONSUMO', upper=True)
    obs = ask('Observação', default='')
    antes = total
    print('\nCONFIRMAÇÃO DA SAÍDA')
    print(f'Produto: {p["nome"]}\nQuantidade: {fmt_qtd(qtd,p["unidade"])} {p["unidade"]}\nLocal: {loc["localizacao"]}\nData consumo: {iso_to_br(data_consumo)}\nTurno: {turno}\nObs: {obs}')
    if not confirm('Confirmar saída?', default=True):
        warn('Saída cancelada. Nada foi salvo.'); pause(); return
    baixar_de_local(p, qtd, loc)
    depois = estoque_total(p['id'])
    execute('''INSERT INTO movimentacoes(produto_id,tipo,quantidade,unidade,localizacao,lote,validade,data_movimento,data_consumo,turno,motivo,observacao,estoque_antes,estoque_depois)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (p['id'],'SAIDA',qtd,p['unidade'],loc['localizacao'],loc['lote'],loc['validade'],data_consumo,data_consumo,turno,motivo,obs,antes,depois))
    evento('SAIDA', f'{p["nome"]}: -{fmt_qtd(qtd,p["unidade"])} {p["unidade"]} de {loc["localizacao"]}')
    ok(f'Saída salva. Estoque atual: {fmt_qtd(depois,p["unidade"])} {p["unidade"]}')
    pause()


def ocorrencia():
    header('PERDAS / SOBRAS / OCORRÊNCIAS')
    p = selecionar_produto()
    if not p: pause(); return
    print('\nTipo de ocorrência:')
    for i,t in enumerate(TIPOS_OCORRENCIA,1): print(f'[{i}] {t}')
    op = ask('Escolha', required=True)
    tipo = TIPOS_OCORRENCIA[int(op)-1] if op.isdigit() and 1 <= int(op) <= len(TIPOS_OCORRENCIA) else 'AJUSTE'
    qtd = ask_float('Quantidade', min_value=0.000001)
    data = pedir_data('Data da ocorrência')
    obs = ask('Observação obrigatória', required=True)
    loc = escolher_local(p, somente_com_estoque=True)
    if not loc: warn('Sem localização com estoque.'); pause(); return
    sinal = 1 if tipo == 'SOBRA' else -1
    antes = estoque_total(p['id'])
    if sinal < 0 and qtd > float(loc['quantidade']):
        warn('Quantidade maior que a disponível na localização.'); pause(); return
    print(f'\nConfirmar {tipo}: {fmt_qtd(qtd,p["unidade"])} {p["unidade"]} | {p["nome"]} | Local {loc["localizacao"]}')
    if not confirm('Confirmar ocorrência?', default=True): warn('Cancelado.'); pause(); return
    execute('UPDATE estoque_locais SET quantidade=quantidade+?, atualizado_em=CURRENT_TIMESTAMP WHERE id=?', (sinal*qtd, loc['id']))
    depois = estoque_total(p['id'])
    execute('''INSERT INTO movimentacoes(produto_id,tipo,quantidade,unidade,localizacao,lote,validade,data_movimento,motivo,observacao,estoque_antes,estoque_depois)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''', (p['id'],tipo,qtd,p['unidade'],loc['localizacao'],loc['lote'],loc['validade'],data,tipo,obs,antes,depois))
    ok('Ocorrência registrada.'); pause()


def historico():
    header('HISTÓRICO')
    rows = fetchall('''SELECT m.id,p.codigo,p.nome,m.tipo,m.quantidade,m.unidade,m.localizacao,m.data_movimento,m.turno,m.observacao,m.estoque_antes,m.estoque_depois
                       FROM movimentacoes m JOIN produtos p ON p.id=m.produto_id ORDER BY m.id DESC LIMIT 150''')
    dados = [(r['id'],r['codigo'],r['nome'],r['tipo'],fmt_qtd(r['quantidade'],r['unidade']),r['unidade'],r['localizacao'],iso_to_br(r['data_movimento']),r['turno'],r['observacao'],fmt_qtd(r['estoque_antes'],r['unidade']),fmt_qtd(r['estoque_depois'],r['unidade'])) for r in rows]
    tabela('ÚLTIMAS MOVIMENTAÇÕES', ['ID','Cod','Produto','Tipo','Qtd','Un','Local','Data','Turno','Obs','Antes','Depois'], dados, 150)
    pause()


def menu_movimentacoes():
    while True:
        op = menu('MOVIMENTAÇÕES', [('1','⚡ Entrada rápida'),('2','⚡ Saída rápida'),('3','Entrada completa'),('4','Saída completa'),('5','Perdas / sobras / ocorrências'),('6','Histórico'),('0','Voltar')])
        if op=='1': entrada_estoque(True)
        elif op=='2': saida_estoque(True)
        elif op=='3': entrada_estoque(False)
        elif op=='4': saida_estoque(False)
        elif op=='5': ocorrencia()
        elif op=='6': historico()
        elif op=='0': break
        else: warn('Opção inválida.'); pause()
