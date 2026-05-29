import zipfile
from pathlib import Path
from configuracao import BASE_DIR, DATA_DIR, REPORTS_DIR, BACKUP_DIR, IMPORT_DIR, PASTA_IMPORTAR, agora_stamp, agora_br
from modulos.banco_dados import evento, init_db
from modulos.interface import header, ok, warn, tabela, ask, confirm, pause, menu, executar_seguro

# Pastas que contêm dados gerados ou recebidos pelo sistema.
# Não há limite artificial de quantidade de arquivos ou tamanho total do histórico.
PASTAS_BACKUP = [DATA_DIR, REPORTS_DIR, IMPORT_DIR, PASTA_IMPORTAR]
PASTAS_PERMITIDAS_RESTAURACAO = {'data', 'relatorios', 'importados', 'importar'}


def _arquivos_backup():
    vistos = set()
    for pasta in PASTAS_BACKUP:
        if not pasta.exists():
            continue
        for arquivo in pasta.rglob('*'):
            if arquivo.is_file():
                real = arquivo.resolve()
                if real not in vistos:
                    vistos.add(real)
                    yield arquivo


def _nome_backup(tipo, data_referencia=None):
    tipo = (tipo or 'completo').lower().strip()
    if tipo == 'diario':
        data_ref = data_referencia or agora_br().strftime('%Y-%m-%d')
        return f'backup_diario_{data_ref}_{agora_stamp()}.zip'
    if tipo == 'mensal':
        data_ref = data_referencia or agora_br().strftime('%Y-%m')
        return f'backup_mensal_{data_ref}_{agora_stamp()}.zip'
    return f'backup_completo_sistema_express_{agora_stamp()}.zip'


def _criar_zip(destino, tipo='completo', data_referencia=None):
    destino.parent.mkdir(parents=True, exist_ok=True)
    arquivos = list(_arquivos_backup())
    with zipfile.ZipFile(destino, 'w', compression=zipfile.ZIP_DEFLATED, allowZip64=True) as z:
        for arquivo in arquivos:
            z.write(arquivo, arquivo.relative_to(BASE_DIR))
        manifesto = (
            'SISTEMA EXCLUSIVO - EXPRESS RESTAURANTES - UNIDADE COLORADO\n'
            f'Tipo de backup: {tipo.upper()}\n'
            f'Data de referência: {data_referencia or "geral"}\n'
            f'Gerado em: {agora_br().strftime("%d/%m/%Y - %H:%M")} -By Maicon\n'
            f'Arquivos protegidos: {len(arquivos)}\n'
            'Conteúdo protegido: banco de dados, relatórios, arquivos importados e pastas de importação.\n'
            'Observação: diário e mensal preservam os dados existentes no momento da geração; não reduzem nem apagam histórico.\n'
        )
        z.writestr('manifesto_backup.txt', manifesto)
    return destino


def _validar_membro_zip(nome):
    caminho = Path(nome)
    if nome == 'manifesto_backup.txt':
        return True
    if caminho.is_absolute() or '..' in caminho.parts:
        return False
    return bool(caminho.parts) and caminho.parts[0] in PASTAS_PERMITIDAS_RESTAURACAO


def _validar_zip(arquivo_zip):
    with zipfile.ZipFile(arquivo_zip, 'r') as z:
        invalido = [m.filename for m in z.infolist() if not _validar_membro_zip(m.filename)]
        if invalido:
            raise RuntimeError('Backup recusado: contém caminho inválido ou inseguro.')
        teste = z.testzip()
        if teste:
            raise RuntimeError(f'Backup corrompido ou ilegível no arquivo interno: {teste}')


def _extrair_zip_seguro(arquivo_zip):
    base = BASE_DIR.resolve()
    _validar_zip(arquivo_zip)
    with zipfile.ZipFile(arquivo_zip, 'r') as z:
        for membro in z.infolist():
            if membro.filename == 'manifesto_backup.txt' or membro.is_dir():
                continue
            destino = (BASE_DIR / membro.filename).resolve()
            try:
                destino.relative_to(base)
            except ValueError:
                raise RuntimeError('Backup recusado: tentativa de extração fora da pasta do sistema.')
            destino.parent.mkdir(parents=True, exist_ok=True)
            with z.open(membro, 'r') as origem, open(destino, 'wb') as saida:
                while True:
                    bloco = origem.read(1024 * 1024)
                    if not bloco:
                        break
                    saida.write(bloco)


def criar_backup(tipo='completo', data_referencia=None, pausar=True):
    titulo = {'completo': 'BACKUP COMPLETO', 'diario': 'BACKUP DIÁRIO', 'mensal': 'BACKUP MENSAL'}.get(tipo, 'BACKUP')
    header(titulo)
    try:
        arquivo = BACKUP_DIR / _nome_backup(tipo, data_referencia)
        _criar_zip(arquivo, tipo=tipo, data_referencia=data_referencia)
        evento('BACKUP', f'Backup {tipo} criado: {arquivo.name}')
        ok(f'Backup criado: {arquivo}')
        return arquivo
    except Exception as e:
        warn(f'Falha ao criar backup: {e}')
        return None
    finally:
        if pausar:
            pause()


def criar_backup_completo():
    return criar_backup('completo')


def criar_backup_diario():
    hoje = agora_br().strftime('%Y-%m-%d')
    data_ref = ask('Data de referência do backup diário no formato AAAA-MM-DD', default=hoje, required=True)
    return criar_backup('diario', data_ref)


def criar_backup_mensal():
    mes = agora_br().strftime('%Y-%m')
    data_ref = ask('Mês de referência do backup mensal no formato AAAA-MM', default=mes, required=True)
    return criar_backup('mensal', data_ref)


def listar_backups():
    header('BACKUPS')
    backs = sorted(BACKUP_DIR.glob('backup*.zip'), reverse=True)
    tabela('BACKUPS DISPONÍVEIS', ['Nº', 'Arquivo', 'Tamanho'], [(i + 1, b.name, f'{b.stat().st_size / 1024:.1f} KB') for i, b in enumerate(backs)], 1000000)
    pause()


def restaurar_backup():
    header('RESTAURAR BACKUP')
    backs = sorted(BACKUP_DIR.glob('backup*.zip'), reverse=True)
    if not backs:
        warn('Nenhum backup encontrado.')
        pause()
        return
    tabela('BACKUPS', ['Nº', 'Arquivo', 'Tamanho'], [(i + 1, b.name, f'{b.stat().st_size / 1024:.1f} KB') for i, b in enumerate(backs)], 1000000)
    op = ask('Número do backup ou 0 para voltar', required=True)
    if op == '0':
        return
    if not op.isdigit() or not (1 <= int(op) <= len(backs)):
        warn('Opção inválida.')
        pause()
        return
    escolhido = backs[int(op) - 1]
    try:
        _validar_zip(escolhido)
    except Exception as e:
        warn(f'Arquivo de backup inválido: {e}')
        pause()
        return
    warn('A restauração substituirá os dados atuais. Será criado um backup completo de segurança antes.')
    if not confirm(f'Restaurar {escolhido.name}?', default=False):
        warn('Cancelado.')
        pause()
        return
    if not confirm('Confirma novamente a restauração?', default=False):
        warn('Cancelado.')
        pause()
        return
    try:
        seguranca = BACKUP_DIR / f'backup_antes_restauracao_{agora_stamp()}.zip'
        _criar_zip(seguranca, tipo='completo', data_referencia='antes_restauracao')
        _extrair_zip_seguro(escolhido)
        init_db()
        evento('BACKUP', f'Restauração concluída: {escolhido.name}')
        ok(f'Restauração concluída. Segurança criada: {seguranca.name}')
    except Exception as e:
        warn(f'Falha na restauração: {e}')
    pause()


def menu_backup():
    while True:
        op = menu('BACKUP / RESTAURAR', [
            ('1', 'Criar backup completo'),
            ('2', 'Criar backup diário'),
            ('3', 'Criar backup mensal'),
            ('4', 'Listar backups'),
            ('5', 'Restaurar backup'),
            ('0', 'Voltar'),
        ])
        if op == '1':
            executar_seguro(criar_backup_completo)
        elif op == '2':
            executar_seguro(criar_backup_diario)
        elif op == '3':
            executar_seguro(criar_backup_mensal)
        elif op == '4':
            executar_seguro(listar_backups)
        elif op == '5':
            executar_seguro(restaurar_backup)
        elif op == '0':
            break
        else:
            warn('Opção inválida.')
            pause()


def backup_automatico_saida():
    try:
        arquivo = BACKUP_DIR / f'backup_saida_segura_{agora_stamp()}.zip'
        return _criar_zip(arquivo, tipo='completo', data_referencia='saida_segura')
    except Exception:
        return None
