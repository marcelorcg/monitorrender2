from telegram import Bot
import os
from dotenv import load_dotenv

load_dotenv()  # lê as variáveis do .env

bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
chat_id = os.getenv("TELEGRAM_CHAT_ID")

bot.send_message(chat_id=chat_id, text="🚀 Teste direto do VS Code: mensagem chegou no Telegram!")
print("Mensagem enviada!")
