#!/usr/bin/env python3
from modulos.banco_dados import init_db, fetchall
from modulos.interface import menu, header, ok, warn, pause, card_grid, divider, executar_seguro
from modulos.produtos import menu_produtos
from modulos.movimentacoes import menu_movimentacoes
from modulos.conferencia import menu_conferencia
from modulos.alertas import painel_alertas, obter_alertas
from modulos.relatorios import menu_relatorios
from modulos.copia_seguranca import menu_backup
from modulos.analitico import menu_analitico
from modulos.funcoes import mostrar_funcoes
from modulos.correria import menu_correria
from modulos.ordem_compra import menu_oc
from modulos.auditoria import menu_auditoria
from modulos.copia_seguranca import backup_automatico_saida
from modulos.codigo_barras import menu_codigo_barras
from modulos.utilitarios import fmt_qtd


def painel():
    header('RESUMO')
    p=fetchall('SELECT COUNT(*) c FROM produtos WHERE ativo=1')[0]['c']
    total_loc=fetchall('SELECT COUNT(*) c FROM estoque_locais WHERE quantidade>0')[0]['c']
    mov=fetchall('SELECT COUNT(*) c FROM movimentacoes')[0]['c']
    baixos=fetchall('''SELECT COUNT(*) c FROM (SELECT p.id,COALESCE(SUM(e.quantidade),0) total,p.estoque_minimo FROM produtos p LEFT JOIN estoque_locais e ON e.produto_id=p.id WHERE p.ativo=1 GROUP BY p.id HAVING p.estoque_minimo>0 AND total<=p.estoque_minimo)''')[0]['c']
    alerts=len(obter_alertas())
    card_grid([
        ('Produtos ativos', p, 'cadastros liberados'),
        ('Locais com estoque', total_loc, 'prateleiras/lotes'),
        ('Movimentações', mov, 'histórico total'),
        ('Abaixo do mínimo', baixos, 'exigem atenção'),
        ('Alertas', alerts, 'painel operacional'),
    ])
    divider('Diagnóstico')
    if alerts: warn('Existem alertas pendentes. Verifique o painel de alertas.')
    else: ok('Operação sem alertas críticos no momento.')
    pause()


def principal():
    init_db()
    while True:
        op=menu('MENU PRINCIPAL', [
            ('1','⚡ Modo correria'),
            ('2','Entrada rápida'),
            ('3','Saída rápida'),
            ('4','Produtos'),
            ('5','Movimentações completas'),
            ('6','Conferência de estoque'),
            ('7','Relatórios'),
            ('8','Alertas'),
            ('9','Planejamento de Produção'),
            ('10','Ordem de Compra'),
            ('11','Backup / Restaurar'),
            ('12','Resumo operacional'),
            ('13','Auditoria'),
            ('14','Funções'),
            ('15','Leitura por código'),
            ('0','Sair')])
        if op=='1': executar_seguro(menu_correria)
        elif op=='2':
            from modulos.movimentacoes import entrada_estoque; executar_seguro(entrada_estoque, True)
        elif op=='3':
            from modulos.movimentacoes import saida_estoque; executar_seguro(saida_estoque, True)
        elif op=='4': executar_seguro(menu_produtos)
        elif op=='5': executar_seguro(menu_movimentacoes)
        elif op=='6': executar_seguro(menu_conferencia)
        elif op=='7': executar_seguro(menu_relatorios)
        elif op=='8': executar_seguro(painel_alertas)
        elif op=='9': executar_seguro(menu_analitico)
        elif op=='10': executar_seguro(menu_oc)
        elif op=='11': executar_seguro(menu_backup)
        elif op=='12': executar_seguro(painel)
        elif op=='13': executar_seguro(menu_auditoria)
        elif op=='14': executar_seguro(mostrar_funcoes)
        elif op=='15': executar_seguro(menu_codigo_barras)
        elif op=='0':
            header('SAIR')
            arq = backup_automatico_saida()
            if arq: ok(f'Backup automático criado: {arq.name}')
            ok('Sistema encerrado com segurança.')
            break
        else: warn('Opção inválida.'); pause()

if __name__ == '__main__':
    try:
        principal()
    except KeyboardInterrupt:
        try:
            arq = backup_automatico_saida()
            print(f'\nSistema interrompido pelo usuário. Dados preservados. Backup: {arq.name if arq else "não gerado"}')
        except Exception:
            print('\nSistema interrompido pelo usuário. Dados preservados.')
    except Exception as e:
        print(f'\nFalha inesperada controlada: {e}')
        try:
            arq = backup_automatico_saida()
            print(f'Backup de segurança: {arq.name if arq else "não gerado"}')
        except Exception:
            pass
