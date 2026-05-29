import os
import shutil
from configuracao import APP_NAME, APP_COMPANY, APP_UNIT, APP_SUBTITLE, assinatura_relatorio

try:
    from rich.console import Console, Group
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt
    from rich import box
    from rich.text import Text
    from rich.align import Align
    from rich.columns import Columns
    RICH_OK = True
except Exception:
    RICH_OK = False
    Console = None

console = Console() if RICH_OK else None

class VoltarMenu(Exception):
    """Sinal interno para cancelar a operação atual ao digitar 999."""
    pass

def executar_seguro(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except VoltarMenu:
        warn('Operação cancelada. Voltando ao menu anterior.')
        pause()
        return None


COR_PRIMARIA = "bright_cyan"
COR_SECUNDARIA = "bright_blue"
COR_DESTAQUE = "bright_yellow"
COR_OK = "bright_green"
COR_ALERTA = "yellow"
COR_ERRO = "bright_red"
COR_TEXTO = "white"
COR_SUAVE = "grey70"


def clear():
    os.system('clear' if os.name != 'nt' else 'cls')


def _largura():
    try:
        return max(70, min(110, shutil.get_terminal_size((92, 24)).columns))
    except Exception:
        return 92


def _linha(char="═"):
    return char * min(_largura(), 96)


def header(titulo=None):
    """Cabeçalho premium, seguro para Termux e com fallback sem Rich."""
    clear()
    titulo = (titulo or "PAINEL").upper()
    if RICH_OK:
        marca = Text()
        marca.append("✦ ", style=COR_DESTAQUE)
        marca.append(APP_NAME, style=f"bold {COR_DESTAQUE}")
        marca.append(" ✦\n", style=COR_DESTAQUE)
        marca.append(APP_COMPANY, style=f"bold {COR_PRIMARIA}")
        marca.append(" — ", style=COR_SUAVE)
        marca.append(APP_UNIT, style=f"bold {COR_OK}")
        marca.append("\n")
        marca.append(APP_SUBTITLE, style=f"bold {COR_TEXTO}")
        rodape = Text(assinatura_relatorio(), style=f"dim {COR_SUAVE}")
        painel = Panel(
            Group(Align.center(marca), Align.center(rodape)),
            title=f"[bold {COR_DESTAQUE}] {titulo} [/bold {COR_DESTAQUE}]",
            border_style=COR_PRIMARIA,
            box=box.DOUBLE,
            padding=(1, 2),
        )
        console.print(painel)
    else:
        print(_linha())
        print(f"{titulo.center(min(_largura(), 96))}")
        print(f"{APP_NAME} - {APP_COMPANY} - {APP_UNIT}")
        print(APP_SUBTITLE)
        print(assinatura_relatorio())
        print(_linha())


def ok(msg):
    console.print(f"[bold {COR_OK}]✅ {msg}[/]") if RICH_OK else print("OK:", msg)


def warn(msg):
    console.print(f"[bold {COR_ALERTA}]⚠ {msg}[/]") if RICH_OK else print("AVISO:", msg)


def error(msg):
    console.print(f"[bold {COR_ERRO}]❌ {msg}[/]") if RICH_OK else print("ERRO:", msg)


def info(msg):
    console.print(f"[bold {COR_PRIMARIA}]ℹ {msg}[/]") if RICH_OK else print("INFO:", msg)


def destaque(msg):
    if RICH_OK:
        console.print(Panel.fit(str(msg), border_style=COR_OK, box=box.ROUNDED, padding=(1, 2)))
    else:
        print(msg)


def divider(titulo=""):
    if RICH_OK:
        if titulo:
            console.rule(f"[bold {COR_DESTAQUE}]{titulo}[/]", style=COR_PRIMARIA)
        else:
            console.rule(style=COR_PRIMARIA)
    else:
        print(_linha("-"))
        if titulo:
            print(titulo)


def card_grid(cards):
    """Mostra cartões de indicadores no painel principal."""
    if not cards:
        return
    if RICH_OK:
        paineis = []
        estilos = [COR_PRIMARIA, COR_OK, COR_DESTAQUE, COR_SECUNDARIA, COR_ALERTA, COR_ERRO]
        for i, (titulo, valor, detalhe) in enumerate(cards):
            corpo = Text()
            corpo.append(str(valor), style=f"bold {estilos[i % len(estilos)]}")
            if detalhe:
                corpo.append(f"\n{detalhe}", style=COR_SUAVE)
            paineis.append(Panel(Align.center(corpo), title=f"[bold]{titulo}[/]", border_style=estilos[i % len(estilos)], box=box.ROUNDED, padding=(1, 2)))
        console.print(Columns(paineis, equal=True, expand=True))
    else:
        for titulo, valor, detalhe in cards:
            print(f"{titulo}: {valor}" + (f" - {detalhe}" if detalhe else ""))


def ask(text, default=None, upper=False, required=False):
    while True:
        if RICH_OK:
            value = Prompt.ask(f"[bold {COR_PRIMARIA}]{text}[/]", default=default if default is not None else None)
        else:
            label = text + (f" [{default}]" if default is not None else "")
            value = input(label + ": ") or (default or "")
        value = str(value).strip()
        if value == '999':
            raise VoltarMenu()
        if upper:
            value = value.upper()
        if required and not value:
            warn("Campo obrigatório.")
            continue
        return value


def ask_float(text, default=None, min_value=None):
    while True:
        raw = ask(text, str(default) if default is not None else None, required=True).replace(',', '.')
        try:
            val = float(raw)
            if min_value is not None and val < min_value:
                warn(f"Valor mínimo permitido: {min_value}")
                continue
            return val
        except Exception:
            error("Digite um número válido. Exemplo: 10 ou 10,500")


def confirm(text, default=True):
    """Confirmação compatível com português e inglês: S/N ou Y/N."""
    sufixo = 'S/n' if default else 's/N'
    while True:
        if RICH_OK:
            raw = Prompt.ask(f"[bold {COR_DESTAQUE}]{text}[/] [{sufixo}]", default='S' if default else 'N')
        else:
            raw = input(f"{text} [{sufixo}]: ") or ('S' if default else 'N')
        raw = str(raw).strip().upper()
        if raw in ('S', 'SIM', 'Y', 'YES'):
            return True
        if raw in ('N', 'NAO', 'NÃO', 'NO'):
            return False
        warn('Digite S para sim ou N para não.')


def pause():
    input("\nPressione ENTER para continuar...")


def menu(titulo, opcoes):
    header(titulo)
    if RICH_OK:
        table = Table(
            title=f"⚙  {titulo}",
            box=box.ROUNDED,
            header_style=f"bold {COR_PRIMARIA}",
            border_style=COR_SECUNDARIA,
            title_style=f"bold {COR_DESTAQUE}",
            show_lines=True,
            expand=True,
        )
        table.add_column("Opção", justify="center", style=f"bold {COR_DESTAQUE}", width=8, no_wrap=True)
        table.add_column("Função", style=f"bold {COR_TEXTO}")
        for k, v in opcoes:
            table.add_row(str(k), str(v))
        console.print(table)
        console.print(f"[dim]{'Digite 999 para voltar ao menu anterior quando estiver em qualquer tela.'}[/]")
        raw = Prompt.ask(f"[bold {COR_PRIMARIA}]Escolha[/]")
    else:
        print(titulo)
        for k, v in opcoes:
            print(f"[{k}] {v}")
        raw = input('Escolha: ')
    raw = str(raw).strip()
    if raw == '999':
        return '0'
    return raw


def tabela(titulo, colunas, linhas, max_rows=80):
    if not linhas:
        warn("Nenhum registro encontrado.")
        return
    if RICH_OK:
        table = Table(
            title=titulo,
            box=box.SIMPLE_HEAVY,
            header_style=f"bold {COR_PRIMARIA}",
            border_style=COR_SECUNDARIA,
            title_style=f"bold {COR_DESTAQUE}",
            expand=True,
            show_lines=False,
        )
        for c in colunas:
            table.add_column(str(c), overflow="fold")
        for idx, r in enumerate(linhas[:max_rows]):
            style = "" if idx % 2 == 0 else "dim"
            table.add_row(*[str(x) if x is not None else "" for x in r], style=style)
        console.print(table)
        if len(linhas) > max_rows:
            warn(f"Mostrando {max_rows} de {len(linhas)} registros.")
    else:
        print("\n" + titulo)
        print(" | ".join(map(str, colunas)))
        for r in linhas[:max_rows]:
            print(" | ".join(str(x) if x is not None else "" for x in r))
