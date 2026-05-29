# SISTEMA EXCLUSIVO - EXPRESS RESTAURANTES - UNIDADE COLORADO

Projeto pronto para gerar APK pelo GitHub Actions usando Buildozer.

## Como usar

1. Envie todos os arquivos deste ZIP para um repositório no GitHub.
2. Entre na aba **Actions**.
3. Abra o workflow **Gerar APK - Sistema Express**.
4. Clique em **Run workflow**.
5. Ao finalizar, baixe o APK em **Artifacts**.

## Arquivo principal do APK

O APK inicia por `main.py`, que abre uma tela Android em formato de console operacional.
O núcleo do sistema permanece em:

```text
sistema - express/iniciar.py
```

## Observações importantes

- O app mantém o padrão profissional do sistema.
- Os dados ficam no ambiente interno do aplicativo Android.
- Para importar arquivos, use as pastas internas do sistema quando estiver usando o APK.
- A versão Termux continua funcionando separadamente com `python iniciar.py` dentro da pasta `sistema - express`.

## Relatórios PDF

Para evitar erro de compilação no Android, este projeto inclui um gerador PDF leve compatível com o sistema. Ele mantém a geração de arquivos PDF sem depender da biblioteca pesada `reportlab` no APK.
