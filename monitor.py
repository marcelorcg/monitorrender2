# monitor.py
import os
import time
from telegram import Bot
from telegram.error import TelegramError

# Pegando as variáveis de ambiente
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("As variáveis TELEGRAM_TOKEN e TELEGRAM_CHAT_ID devem estar definidas!")

bot = Bot(token=TELEGRAM_TOKEN)

def enviar_mensagem(texto):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=texto)
        print(f"Mensagem enviada: {texto}")
    except TelegramError as e:
        print(f"Erro ao enviar mensagem: {e}")

# Mensagem inicial
enviar_mensagem("Bot iniciado com sucesso! 🚀")

# Loop principal: envia uma mensagem de teste a cada X segundos
while True:
    try:
        enviar_mensagem("Teste de funcionamento 24h ⏳")
        time.sleep(3600)  # aguarda 1 hora (3600 segundos)
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        time.sleep(60)  # espera 1 minuto antes de tentar novamente
