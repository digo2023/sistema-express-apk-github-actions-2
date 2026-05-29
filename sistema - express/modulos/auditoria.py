from modulos.banco_dados import fetchall
from modulos.interface import header, tabela, pause, menu, warn


def historico_eventos():
    header('AUDITORIA OPERACIONAL')
    rows = fetchall('SELECT id,tipo,descricao,criado_em FROM eventos ORDER BY id DESC LIMIT 300')
    dados = [(r['id'], r['tipo'], r['descricao'], r['criado_em']) for r in rows]
    tabela('ÚLTIMOS EVENTOS DO SISTEMA', ['ID','Tipo','Descrição','Data/Hora'], dados, 300)
    pause()


def menu_auditoria():
    while True:
        op = menu('AUDITORIA', [('1','Ver histórico operacional'),('0','Voltar')])
        if op == '1': historico_eventos()
        elif op == '0': break
        else: warn('Opção inválida.'); pause()
