import os
from telegram import Bot

# 🚀 Pega variáveis de ambiente do Railway
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

bot = Bot(token=TELEGRAM_TOKEN)

# 🔹 Mensagem de teste
bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="Teste de integração Railway ✅")

print("Mensagem de teste enviada ao Telegram!")
