from modulos.interface import header, ask, ask_float, confirm, ok, warn, pause, menu, info, executar_seguro
from modulos.banco_dados import execute, fetchone, evento
from modulos.utilitarios import buscar_produto_por_barra, selecionar_produto, pedir_data, pedir_turno, fmt_qtd, estoque_total, escolher_local, iso_to_br
from modulos.movimentacoes import upsert_local, baixar_de_local


def pedir_codigo():
    info('Leia o código com leitor Bluetooth/app de scanner ou digite manualmente. O código será tratado como texto.')
    cod = ask('Código de barras / EAN / código interno', required=True)
    return ''.join(ch for ch in cod.strip() if ch.isalnum() or ch in '.-_')


def encontrar_por_codigo():
    cod = pedir_codigo()
    p = buscar_produto_por_barra(cod)
    if p:
        return p, cod
    warn('Código não encontrado no cadastro.')
    if confirm('Deseja vincular este código a um produto existente?', default=True):
        prod = selecionar_produto()
        if not prod:
            return None, cod
        existente = fetchone('SELECT codigo,nome FROM produtos WHERE codigo_barras=? AND ativo=1', (cod,))
        if existente:
            warn(f'Código já está vinculado a {existente["codigo"]} - {existente["nome"]}.')
            pause(); return None, cod
        if confirm(f'Vincular código {cod} ao produto {prod["nome"]}?', default=True):
            execute('UPDATE produtos SET codigo_barras=?, atualizado_em=CURRENT_TIMESTAMP WHERE id=?', (cod, prod['id']))
            evento('PRODUTO', f'Código de barras vinculado: {cod} -> {prod["codigo"]} {prod["nome"]}')
            ok('Código vinculado com sucesso.')
            return buscar_produto_por_barra(cod), cod
    return None, cod


def vincular_codigo():
    header('VINCULAR CÓDIGO DE BARRAS')
    prod = selecionar_produto()
    if not prod: pause(); return
    cod = pedir_codigo()
    existente = fetchone('SELECT id,codigo,nome FROM produtos WHERE codigo_barras=? AND ativo=1', (cod,))
    if existente and int(existente['id']) != int(prod['id']):
        warn(f'Código já está vinculado a {existente["codigo"]} - {existente["nome"]}.')
        pause(); return
    print(f'Produto: {prod["codigo"]} - {prod["nome"]}\nCódigo de barras: {cod}')
    if confirm('Confirmar vínculo?', default=True):
        execute('UPDATE produtos SET codigo_barras=?, atualizado_em=CURRENT_TIMESTAMP WHERE id=?', (cod, prod['id']))
        evento('PRODUTO', f'Código de barras vinculado: {cod} -> {prod["codigo"]} {prod["nome"]}')
        ok('Vínculo salvo.')
    pause()


def consultar_codigo():
    header('CONSULTAR POR CÓDIGO')
    p, cod = encontrar_por_codigo()
    if not p: pause(); return
    total = estoque_total(p['id'])
    print(f'Código lido: {cod}\nProduto: {p["codigo"]} - {p["nome"]}\nCategoria: {p["categoria"]}\nUnidade: {p["unidade"]}\nEstoque total: {fmt_qtd(total,p["unidade"])} {p["unidade"]}')
    pause()


def entrada_por_codigo():
    header('ENTRADA POR CÓDIGO')
    p, cod = encontrar_por_codigo()
    if not p: pause(); return
    print(f'Produto encontrado: {p["codigo"]} | {p["nome"]} | Unidade: {p["unidade"]}')
    qtd = ask_float('Quantidade recebida', min_value=0.000001)
    local = ask('Localização / prateleira', default='GERAL', upper=True, required=True)
    lote = ask('Lote', default='', upper=True)
    validade = pedir_data('Validade (ENTER para deixar vazio)', default_hoje=False, obrigatoria=False)
    data_mov = pedir_data('Data da entrada')
    motivo = ask('Motivo/Fornecedor/NF', default='ENTRADA POR CODIGO', upper=True)
    obs = ask('Observação', default='')
    antes = estoque_total(p['id'])
    print(f'\nCONFIRMAÇÃO DA ENTRADA\nProduto: {p["nome"]}\nQuantidade: {fmt_qtd(qtd,p["unidade"])} {p["unidade"]}\nLocal: {local}\nLote: {lote}\nValidade: {iso_to_br(validade)}\nData: {iso_to_br(data_mov)}')
    if not confirm('Confirmar entrada?', default=True):
        warn('Entrada cancelada. Nada foi salvo.'); pause(); return
    upsert_local(p['id'], local, lote, validade, qtd)
    depois = estoque_total(p['id'])
    execute('''INSERT INTO movimentacoes(produto_id,tipo,quantidade,unidade,localizacao,lote,validade,data_movimento,motivo,observacao,estoque_antes,estoque_depois)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''', (p['id'],'ENTRADA',qtd,p['unidade'],local,lote,validade,data_mov,motivo,obs,antes,depois))
    evento('ENTRADA', f'{p["nome"]}: +{fmt_qtd(qtd,p["unidade"])} {p["unidade"]} por código {cod}')
    ok(f'Entrada salva. Estoque atual: {fmt_qtd(depois,p["unidade"])} {p["unidade"]}')
    pause()


def saida_por_codigo():
    header('SAÍDA POR CÓDIGO')
    p, cod = encontrar_por_codigo()
    if not p: pause(); return
    total = estoque_total(p['id'])
    print(f'Produto: {p["nome"]} | Disponível total: {fmt_qtd(total,p["unidade"])} {p["unidade"]}')
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
    motivo = ask('Motivo', default='CONSUMO POR CODIGO', upper=True)
    obs = ask('Observação', default='')
    antes = total
    print(f'\nCONFIRMAÇÃO DA SAÍDA\nProduto: {p["nome"]}\nQuantidade: {fmt_qtd(qtd,p["unidade"])} {p["unidade"]}\nLocal: {loc["localizacao"]}\nData consumo: {iso_to_br(data_consumo)}\nTurno: {turno}')
    if not confirm('Confirmar saída?', default=True):
        warn('Saída cancelada. Nada foi salvo.'); pause(); return
    baixar_de_local(p, qtd, loc)
    depois = estoque_total(p['id'])
    execute('''INSERT INTO movimentacoes(produto_id,tipo,quantidade,unidade,localizacao,lote,validade,data_movimento,data_consumo,turno,motivo,observacao,estoque_antes,estoque_depois)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (p['id'],'SAIDA',qtd,p['unidade'],loc['localizacao'],loc['lote'],loc['validade'],data_consumo,data_consumo,turno,motivo,obs,antes,depois))
    evento('SAIDA', f'{p["nome"]}: -{fmt_qtd(qtd,p["unidade"])} {p["unidade"]} por código {cod}')
    ok(f'Saída salva. Estoque atual: {fmt_qtd(depois,p["unidade"])} {p["unidade"]}')
    pause()


def conferencia_por_codigo():
    header('CONFERÊNCIA POR CÓDIGO')
    p, cod = encontrar_por_codigo()
    if not p: pause(); return
    loc = escolher_local(p, somente_com_estoque=False)
    if not loc:
        warn('Produto ainda não possui localização cadastrada. Faça uma entrada primeiro.'); pause(); return
    sistema = float(loc['quantidade'])
    print(f'Produto: {p["nome"]}\nLocal: {loc["localizacao"]}\nSistema: {fmt_qtd(sistema,p["unidade"])} {p["unidade"]}')
    fisico = ask_float('Quantidade física encontrada', min_value=0)
    diff = fisico - sistema
    data = pedir_data('Data da conferência')
    obs = ask('Observação obrigatória', required=True)
    print(f'Diferença: {fmt_qtd(diff,p["unidade"])} {p["unidade"]}')
    ajustar = abs(diff) > 0 and confirm('Ajustar estoque para a quantidade física?', default=False)
    execute('''INSERT INTO conferencias(produto_id,localizacao,quantidade_sistema,quantidade_fisica,diferenca,ajustado,data_conferencia,observacao)
               VALUES(?,?,?,?,?,?,?,?)''', (p['id'],loc['localizacao'],sistema,fisico,diff,1 if ajustar else 0,data,obs))
    if ajustar:
        antes_total = estoque_total(p['id'])
        execute('UPDATE estoque_locais SET quantidade=?, atualizado_em=CURRENT_TIMESTAMP WHERE id=?', (fisico, loc['id']))
        depois_total = estoque_total(p['id'])
        execute('''INSERT INTO movimentacoes(produto_id,tipo,quantidade,unidade,localizacao,lote,validade,data_movimento,motivo,observacao,estoque_antes,estoque_depois)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''', (p['id'],'AJUSTE_CONFERENCIA',abs(diff),p['unidade'],loc['localizacao'],loc['lote'],loc['validade'],data,'CONFERENCIA POR CODIGO',obs,antes_total,depois_total))
        ok('Conferência registrada e estoque ajustado.')
    else:
        ok('Conferência registrada sem ajuste.')
    evento('CONFERENCIA', f'{p["nome"]} | {loc["localizacao"]} | diferença {fmt_qtd(diff,p["unidade"])} por código {cod}')
    pause()


def menu_codigo_barras():
    while True:
        op = menu('LEITURA POR CÓDIGO', [
            ('1','Entrada por código'),
            ('2','Saída por código'),
            ('3','Conferência por código'),
            ('4','Vincular código de barras a produto'),
            ('5','Consultar produto por código'),
            ('0','Voltar')])
        if op=='1': executar_seguro(entrada_por_codigo)
        elif op=='2': executar_seguro(saida_por_codigo)
        elif op=='3': executar_seguro(conferencia_por_codigo)
        elif op=='4': executar_seguro(vincular_codigo)
        elif op=='5': executar_seguro(consultar_codigo)
        elif op=='0': break
        else: warn('Opção inválida.'); pause()
