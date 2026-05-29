from modulos.interface import menu, warn, pause, header, ok


def menu_correria():
    while True:
        op = menu('MODO CORRERIA', [
            ('1','Entrada rápida'),
            ('2','Saída rápida'),
            ('3','Consultar estoque'),
            ('4','Conferência rápida'),
            ('5','Alertas imediatos'),
            ('6','Backup agora'),
            ('0','Voltar')
        ])
        if op == '1':
            from modulos.movimentacoes import entrada_estoque; entrada_estoque(True)
        elif op == '2':
            from modulos.movimentacoes import saida_estoque; saida_estoque(True)
        elif op == '3':
            from modulos.relatorios import estoque_tela; estoque_tela()
        elif op == '4':
            from modulos.conferencia import nova_conferencia; nova_conferencia()
        elif op == '5':
            from modulos.alertas import painel_alertas; painel_alertas()
        elif op == '6':
            from modulos.copia_seguranca import criar_backup; criar_backup(pausar=True)
        elif op == '0':
            break
        else:
            warn('Opção inválida.'); pause()
