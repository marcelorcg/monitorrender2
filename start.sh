#!/bin/bash
echo "🚀 Iniciando monitoramento diário na nuvem..."

# Garante que o Python e pip estão funcionando
python3 --version
pip3 --version

# Instala automaticamente as dependências do requirements.txt
pip3 install -r requirements.txt --quiet

# Executa o monitor principal
python3 monitor.py
