from modulos.interface import header, pause


def mostrar_funcoes():
    header('FUNÇÕES')
    print('''
FUNÇÕES DO SISTEMA — SISTEMA EXCLUSIVO - EXPRESS RESTAURANTES - UNIDADE COLORADO

1. MODO CORRERIA
Atalho para as ações mais usadas no dia a dia: entrada rápida, saída rápida, consulta de estoque, conferência, alertas e backup.

2. PRODUTOS
Cadastre o produto uma única vez. A quantidade por prateleira, câmara, freezer ou estoque reserva é controlada nas entradas. Use a opção Cadastro automático para ler um arquivo Tekinisa e cadastrar somente os produtos novos, sem duplicar códigos já existentes.

3. ENTRADA RÁPIDA
Use para lançar insumos em poucos segundos. O sistema pede produto, quantidade, localização, data e confirmação antes de salvar.

4. SAÍDA RÁPIDA
Use para baixa diária. Sempre pede data de consumo e turno: A = Almoço, B = Janta, C = Ceia. O sistema bloqueia saída maior que o estoque.

5. CONFERÊNCIA
Compare a quantidade do sistema com a quantidade física por localização. Ajustes exigem confirmação e observação.

6. PLANEJAMENTO DE PRODUÇÃO
Importe a Requisição Analítica Tekinisa, gere o relatório de necessários por período/turno, importe a Ordem de Compra Tekinisa e confira Necessários x Ordem de Compra. O estoque atual fica como consulta auxiliar de margem de segurança.

7. RELATÓRIO DE FALTANTES
O fluxo principal cruza o necessário do planejamento com a Ordem de Compra Tekinisa, apontando itens faltantes, quantidade insuficiente, OK COM SOBRA e itens da OC sem uso no período.

8. ORDEM DE COMPRA
Importe ou cadastre a OC e confira Necessários x Ordem de Compra. O estoque atual permanece como consulta auxiliar de margem de segurança.

9. RELATÓRIOS
Gere estoque completo ou somente estoque com saldo. Produtos aparecem em ordem alfabética e itens zerados podem ser excluídos do relatório quando desejar.

10. LEITURA POR CÓDIGO
Permite entrada, saída, conferência, consulta e vínculo de código de barras/EAN. Funciona digitando, colando, usando leitor Bluetooth ou aplicativo de scanner que envie o código para o Termux.

11. SELEÇÃO DE ARQUIVOS
Arquivos podem ser copiados para as pastas importar/analiticos, importar/ordens_compra e importar/backups. O sistema lista os arquivos e permite escolher pelo número, evitando digitar caminhos longos.

12. VOLTAR COM 999
Em menus, cadastros e perguntas, digite 999 para voltar ou cancelar a operação atual sem salvar dados parciais.

13. BACKUP
Use backup completo, diário ou mensal conforme a rotina. Todos preservam os dados existentes no momento da geração. O sistema também cria backup automático ao sair com segurança.

REGRA DE OURO:
Entrou, lançou. Saiu, baixou. Conferiu, registrou. Divergiu, explicou. Fechou o dia, fez backup.
''')
    pause()
