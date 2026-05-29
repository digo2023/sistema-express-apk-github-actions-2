from pathlib import Path
from configuracao import PASTA_ANALITICOS, PASTA_ORDENS_COMPRA, PASTA_BACKUPS_IMPORTAR, PASTA_OUTROS_IMPORTAR
from modulos.interface import header, ask, warn, tabela, info

PASTAS = {
    'analitico': PASTA_ANALITICOS,
    'oc': PASTA_ORDENS_COMPRA,
    'backup': PASTA_BACKUPS_IMPORTAR,
    'outros': PASTA_OUTROS_IMPORTAR,
}
EXTENSOES = {
    'analitico': ['.pdf'],
    'oc': ['.pdf', '.csv'],
    'backup': ['.zip'],
    'outros': ['.pdf', '.csv', '.xlsx', '.xls', '.zip', '.xml'],
}

def _listar(pasta, exts):
    pasta.mkdir(parents=True, exist_ok=True)
    itens = []
    for ext in exts:
        itens.extend(pasta.glob(f'*{ext}'))
        itens.extend(pasta.glob(f'*{ext.upper()}'))
    return sorted({x.resolve() for x in itens}, key=lambda x: x.name.lower())

def selecionar_arquivo(tipo='outros', titulo='SELECIONAR ARQUIVO'):
    pasta = PASTAS.get(tipo, PASTA_OUTROS_IMPORTAR)
    exts = EXTENSOES.get(tipo, EXTENSOES['outros'])
    while True:
        header(titulo)
        info(f'Pasta de importação: {pasta}')
        arquivos = _listar(pasta, exts)
        if arquivos:
            tabela('ARQUIVOS ENCONTRADOS', ['Nº', 'Arquivo', 'Tamanho'], [(i+1, a.name, f'{a.stat().st_size/1024:.1f} KB') for i,a in enumerate(arquivos)], 1000000)
        else:
            warn('Nenhum arquivo encontrado nesta pasta.')
        print('\n1 - Escolher arquivo da pasta de importação')
        print('2 - Digitar caminho manualmente')
        print('999 - Voltar')
        op = ask('Escolha', required=True)
        if op == '1':
            if not arquivos:
                warn('Copie o arquivo para a pasta indicada acima e tente novamente.')
                continue
            num = ask('Número do arquivo', required=True)
            if num.isdigit() and 1 <= int(num) <= len(arquivos):
                return str(arquivos[int(num)-1])
            warn('Número inválido.')
        elif op == '2':
            caminho = ask('Caminho completo do arquivo', required=True)
            p = Path(caminho)
            if p.exists() and p.is_file():
                return str(p)
            warn('Arquivo não encontrado.')
        else:
            warn('Opção inválida.')
