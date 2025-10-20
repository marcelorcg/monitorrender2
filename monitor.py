import os
import requests
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

# 🔹 Variáveis do Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=TELEGRAM_TOKEN)

def enviar_telegram(mensagem):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=mensagem)
        print("✅ Mensagem enviada no Telegram!")
    except Exception as e:
        print(f"⚠️ Erro ao enviar mensagem: {e}")

def main():
    # 🔹 Modo teste: envia mensagem de teste mesmo sem alteração
    enviar_telegram("🚀 Teste rápido: monitor funcionando normalmente!")

    # Aqui você mantém o código normal do monitor (verificação das URLs)
    urls = [
        os.getenv("URL1"),
        os.getenv("URL2")
    ]

    for url in urls:
        try:
            response = requests.get(url)
            response.raise_for_status()
            print(f"⏳ Verificando {url}... OK")
        except requests.HTTPError as http_err:
            print(f"⚠️ HTTP Error ao acessar {url}: {http_err}")
            enviar_telegram(f"⚠️ HTTP Error ao acessar {url}: {http_err}")
        except Exception as e:
            print(f"⚠️ Erro ao acessar {url}: {e}")
            enviar_telegram(f"⚠️ Erro ao acessar {url}: {e}")

if __name__ == "__main__":
    main()
