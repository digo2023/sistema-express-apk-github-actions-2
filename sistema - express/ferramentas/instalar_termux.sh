#!/data/data/com.termux/files/usr/bin/bash
set -e
pkg update -y
pkg install python python-pip zip unzip nano poppler -y
pip install -r bibliotecas.txt
pip install -r bibliotecas-analitico.txt
echo "Instalação concluída. Execute: python iniciar.py"
