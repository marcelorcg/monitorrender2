#!/bin/bash
# start.sh - inicia o monitor diário no Railway (modo síncrono confiável)

echo "🚀 Iniciando monitoramento diário 24h (modo síncrono confiável)..."

# Executa o monitor.py diretamente e aguarda até terminar
python monitor.py

echo "✅ Monitoramento concluído com sucesso!"
