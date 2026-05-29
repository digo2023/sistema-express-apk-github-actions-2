# -*- coding: utf-8 -*-
"""
Aplicativo Android do SISTEMA EXCLUSIVO - EXPRESS RESTAURANTES - UNIDADE COLORADO.
Este arquivo é apenas a interface de execução para APK. O sistema operacional continua em
"sistema - express/iniciar.py" com o banco e os módulos originais preservados.
"""
import os
import re
import sys
import time
import queue
import threading
import traceback
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup

ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
ROOT_DIR = Path(__file__).resolve().parent
SISTEMA_DIR = ROOT_DIR / "sistema - express"


class EntradaTerminal:
    def __init__(self):
        self._fila = queue.Queue()

    def enviar(self, texto: str):
        if texto is None:
            texto = ""
        self._fila.put(str(texto) + "\n")

    def readline(self):
        return self._fila.get()

    def readable(self):
        return True


class SaidaTerminal:
    def __init__(self, callback):
        self.callback = callback
        self._buffer = ""

    def write(self, texto):
        if not texto:
            return 0
        texto = ANSI_RE.sub("", str(texto))
        self._buffer += texto
        # envia em blocos para não travar a interface com caractere por caractere
        if "\n" in self._buffer or len(self._buffer) > 180:
            parte = self._buffer
            self._buffer = ""
            self.callback(parte)
        return len(texto)

    def flush(self):
        if self._buffer:
            parte = self._buffer
            self._buffer = ""
            self.callback(parte)

    def isatty(self):
        return False


class TelaPrincipal(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(6), padding=dp(8), **kwargs)
        Window.clearcolor = (0.03, 0.05, 0.08, 1)
        self.entrada_terminal = EntradaTerminal()
        self.executando = False
        self.thread_sistema = None
        self.linhas = []
        self.max_linhas_interface = 4500

        topo = Label(
            text="SISTEMA EXCLUSIVO\nEXPRESS RESTAURANTES — UNIDADE COLORADO",
            color=(1, 0.86, 0.25, 1),
            bold=True,
            font_size="18sp",
            size_hint_y=None,
            height=dp(58),
            halign="center",
            valign="middle",
        )
        topo.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        self.add_widget(topo)

        self.scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self.saida = Label(
            text="Toque em INICIAR SISTEMA para abrir o painel operacional.\n",
            color=(0.92, 0.96, 1, 1),
            font_name="RobotoMono-Regular" if Path("RobotoMono-Regular.ttf").exists() else "Roboto",
            font_size="12sp",
            markup=False,
            size_hint_y=None,
            halign="left",
            valign="top",
        )
        self.saida.bind(texture_size=self._ajustar_altura)
        self.scroll.add_widget(self.saida)
        self.add_widget(self.scroll)

        barra = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(48), spacing=dp(6))
        self.campo = TextInput(
            hint_text="Digite a opção ou informação solicitada...",
            multiline=False,
            font_size="16sp",
            foreground_color=(1, 1, 1, 1),
            background_color=(0.08, 0.11, 0.16, 1),
            cursor_color=(1, 0.86, 0.25, 1),
        )
        self.campo.bind(on_text_validate=self.enviar_linha)
        barra.add_widget(self.campo)

        botao_enviar = Button(text="ENVIAR", size_hint_x=None, width=dp(92), bold=True)
        botao_enviar.bind(on_release=self.enviar_linha)
        barra.add_widget(botao_enviar)
        self.add_widget(barra)

        botoes = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(44), spacing=dp(6))
        self.botao_iniciar = Button(text="INICIAR SISTEMA", bold=True)
        self.botao_iniciar.bind(on_release=self.iniciar_sistema)
        botoes.add_widget(self.botao_iniciar)

        botao_voltar = Button(text="999 VOLTAR")
        botao_voltar.bind(on_release=lambda *_: self._enviar_texto("999"))
        botoes.add_widget(botao_voltar)

        botao_enter = Button(text="ENTER")
        botao_enter.bind(on_release=lambda *_: self._enviar_texto(""))
        botoes.add_widget(botao_enter)
        self.add_widget(botoes)

        self._pedir_permissoes_android()

    def _ajustar_altura(self, *_):
        self.saida.text_size = (self.scroll.width - dp(16), None)
        self.saida.height = max(self.saida.texture_size[1] + dp(20), self.scroll.height)

    def _append_ui(self, texto):
        self.linhas.extend(str(texto).splitlines(True))
        if len(self.linhas) > self.max_linhas_interface:
            self.linhas = self.linhas[-self.max_linhas_interface:]
        self.saida.text = "".join(self.linhas)
        Clock.schedule_once(lambda *_: setattr(self.scroll, "scroll_y", 0), 0.05)

    def escrever(self, texto):
        Clock.schedule_once(lambda *_: self._append_ui(texto), 0)

    def _pedir_permissoes_android(self):
        try:
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
            ])
        except Exception:
            pass

    def iniciar_sistema(self, *_):
        if self.executando:
            self.escrever("\nSistema já está em execução.\n")
            return
        if not (SISTEMA_DIR / "iniciar.py").exists():
            self._popup("Falha", "Arquivo sistema - express/iniciar.py não encontrado no APK.")
            return
        self.executando = True
        self.botao_iniciar.disabled = True
        self.escrever("\nIniciando sistema...\n")
        self.thread_sistema = threading.Thread(target=self._executar_sistema, daemon=True)
        self.thread_sistema.start()

    def _executar_sistema(self):
        entrada_original = sys.stdin
        saida_original = sys.stdout
        erro_original = sys.stderr
        cwd_original = os.getcwd()
        saida = SaidaTerminal(self.escrever)
        try:
            sys.stdin = self.entrada_terminal
            sys.stdout = saida
            sys.stderr = saida
            sys.path.insert(0, str(SISTEMA_DIR))
            os.chdir(str(SISTEMA_DIR))
            namespace = {"__name__": "__main__", "__file__": str(SISTEMA_DIR / "iniciar.py")}
            codigo = (SISTEMA_DIR / "iniciar.py").read_text(encoding="utf-8")
            exec(compile(codigo, str(SISTEMA_DIR / "iniciar.py"), "exec"), namespace)
        except SystemExit:
            pass
        except Exception:
            traceback.print_exc()
        finally:
            try:
                saida.flush()
            except Exception:
                pass
            sys.stdin = entrada_original
            sys.stdout = saida_original
            sys.stderr = erro_original
            try:
                os.chdir(cwd_original)
            except Exception:
                pass
            self.executando = False
            Clock.schedule_once(lambda *_: setattr(self.botao_iniciar, "disabled", False), 0)
            self.escrever("\nSistema finalizado.\n")

    def enviar_linha(self, *_):
        texto = self.campo.text
        self.campo.text = ""
        self._enviar_texto(texto)

    def _enviar_texto(self, texto):
        self.escrever(f"{texto}\n")
        self.entrada_terminal.enviar(texto)

    def _popup(self, titulo, msg):
        pop = Popup(title=titulo, content=Label(text=msg), size_hint=(0.9, 0.35))
        pop.open()


class SistemaExpressApp(App):
    title = "Sistema Express"

    def build(self):
        return TelaPrincipal()


if __name__ == "__main__":
    SistemaExpressApp().run()
