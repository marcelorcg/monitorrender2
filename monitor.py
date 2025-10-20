import os
import requests

from telegram import Bot

# Pega variáveis de ambiente do Railway
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=TELEGRAM_TOKEN)

bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="🚀 Teste: mensagem chegou no Telegram!")
print("Mensagem enviada com sucesso!")
