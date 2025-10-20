import os
import requests
from bs4 import BeautifulSoup
import time

from telegram import Bot
from telegram.error import TelegramError

# 🔹 Variáveis do Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=TELEGRAM_TOKEN)

# 🔹 URLs que você quer monitorar
URLS = [
    os.getenv("URL1"),
    os.getenv("URL2")
]

# 🔹 Função para enviar mensagem
def enviar_telegram(mensagem: str):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=mensagem)
        print("✅ Mensagem enviada no Telegram!")
    except TelegramError as e:
        print(f"⚠️ Erro ao enviar mensagem: {e}")

# 🔹 Função para checar sites
def checar_sites():
    for url in URLS:
        try:
            res = requests.get(url, timeout=15)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "html.parser")
            # Envia conteúdo resumido ou apenas aviso
            enviar_telegram(f"Teste de monitor: site acessado com sucesso!\nURL: {url}\nConteúdo inicial:\n{soup.get_text()[:200]}...")
        except requests.HTTPError as e:
            enviar_telegram(f"⚠️ HTTP Error ao acessar {url}: {e}")
        except requests.RequestException as e:
            enviar_telegram(f"⚠️ Erro ao acessar {url}: {e}")

# 🔹 Executa o monitor uma vez para teste
if __name__ == "__main__":
    print("🚀 Monitor de teste iniciado!")
    checar_sites()
    print("✅ Monitor de teste concluído!")
