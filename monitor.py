import os
import requests
from datetime import datetime
from bs4 import BeautifulSoup

# 🔹 Configurações do Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 🔹 URLs para monitorar
URLS = [
    os.getenv("URL1"),
    os.getenv("URL2")
]

def enviar_telegram(mensagem):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Variáveis TELEGRAM não configuradas.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensagem}
    try:
        requests.post(url, data=payload)
        print(f"📩 Mensagem enviada: {mensagem}")
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem: {e}")

# 🔹 Rodando o monitor
print("🚀 Monitoramento diário iniciado!")

for url in URLS:
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        mensagem = f"Teste do monitor: {url}\nExecutado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        enviar_telegram(mensagem)
    except requests.HTTPError as http_err:
        print(f"⚠️ Erro HTTP: {http_err} - {url}")
    except Exception as e:
        print(f"❌ Erro ao acessar {url}: {e}")

print("✅ Monitoramento concluído!")
