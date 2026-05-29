from modulos.banco_dados import execute, fetchall, evento
from modulos.interface import header, ask, ask_float, confirm, ok, warn, tabela, pause, menu
from modulos.utilitarios import selecionar_produto, escolher_local, pedir_data, fmt_qtd, iso_to_br, estoque_total


def nova_conferencia():
    header('CONFERÊNCIA DE ESTOQUE')
    p = selecionar_produto()
    if not p: pause(); return
    loc = escolher_local(p, somente_com_estoque=False)
    if not loc:
        warn('Produto ainda não possui localização cadastrada. Faça uma entrada primeiro.'); pause(); return
    sistema = float(loc['quantidade'])
    print(f"Produto: {p['nome']}\nLocal: {loc['localizacao']}\nSistema: {fmt_qtd(sistema,p['unidade'])} {p['unidade']}")
    fisico = ask_float('Quantidade física encontrada', min_value=0)
    diff = fisico - sistema
    data = pedir_data('Data da conferência')
    obs = ask('Observação obrigatória', required=True)
    print(f'Diferença: {fmt_qtd(diff,p["unidade"])} {p["unidade"]}')
    ajustar = abs(diff) > 0 and confirm('Ajustar estoque para a quantidade física? [y/n]', default=False)
    execute('''INSERT INTO conferencias(produto_id,localizacao,quantidade_sistema,quantidade_fisica,diferenca,ajustado,data_conferencia,observacao)
               VALUES(?,?,?,?,?,?,?,?)''', (p['id'],loc['localizacao'],sistema,fisico,diff,1 if ajustar else 0,data,obs))
    if ajustar:
        antes_total = estoque_total(p['id'])
        execute('UPDATE estoque_locais SET quantidade=?, atualizado_em=CURRENT_TIMESTAMP WHERE id=?', (fisico, loc['id']))
        depois_total = estoque_total(p['id'])
        execute('''INSERT INTO movimentacoes(produto_id,tipo,quantidade,unidade,localizacao,lote,validade,data_movimento,motivo,observacao,estoque_antes,estoque_depois)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''', (p['id'],'AJUSTE_CONFERENCIA',abs(diff),p['unidade'],loc['localizacao'],loc['lote'],loc['validade'],data,'CONFERENCIA',obs,antes_total,depois_total))
        ok('Conferência registrada e estoque ajustado.')
    else: ok('Conferência registrada sem ajuste.')
    evento('CONFERENCIA', f'{p["nome"]} | {loc["localizacao"]} | diferença {fmt_qtd(diff,p["unidade"])}')
    pause()


def historico_conferencias():
    header('HISTÓRICO DE CONFERÊNCIAS')
    rows = fetchall('''SELECT c.id,p.codigo,p.nome,c.localizacao,c.quantidade_sistema,c.quantidade_fisica,c.diferenca,c.ajustado,c.data_conferencia,c.observacao
                       FROM conferencias c JOIN produtos p ON p.id=c.produto_id ORDER BY c.id DESC LIMIT 150''')
    dados = [(r['id'],r['codigo'],r['nome'],r['localizacao'],fmt_qtd(r['quantidade_sistema']),fmt_qtd(r['quantidade_fisica']),fmt_qtd(r['diferenca']),'SIM' if r['ajustado'] else 'NAO',iso_to_br(r['data_conferencia']),r['observacao']) for r in rows]
    tabela('CONFERÊNCIAS', ['ID','Cod','Produto','Local','Sistema','Físico','Dif','Ajustado','Data','Obs'], dados, 150)
    pause()


def menu_conferencia():
    while True:
        op = menu('CONFERÊNCIA', [('1','Nova conferência por localização'),('2','Histórico'),('0','Voltar')])
        if op=='1': nova_conferencia()
        elif op=='2': historico_conferencias()
        elif op=='0': break
        else: warn('Opção inválida.'); pause()
