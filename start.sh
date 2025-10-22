#!/bin/bash
# start.sh - inicia o monitor diário no Railway

echo "🚀 Iniciando monitoramento diário 24h..."
# Ativa o ambiente virtual se existir
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Executa o monitor.py
python monitor.py
