import os
import requests
from bs4 import BeautifulSoup
from hashlib import sha256
from datetime import datetime
from time import sleep
from dotenv import load_dotenv
from telegram import Bot

# Carrega variáveis do .env (ou do Railway)
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
URLS = [
    "https://www.cacapava.sp.gov.br/publicacoes",
    "https://www.camarasjc.sp.gov.br/a-camara/concurso-publico.php"
]

# Arquivo para armazenar hash anterior
HASH_FILE = "hash_antigo.txt"

# Inicializa bot do Telegram
bot = Bot(token=BOT_TOKEN) if BOT_TOKEN and CHAT_ID else None

def get_hash(content: str) -> str:
    return sha256(content.encode("utf-8")).hexdigest()

def enviar_telegram(mensagem: str):
    if bot:
        bot.send_message(chat_id=CHAT_ID, text=mensagem)
        print("✅ Mensagem enviada no Telegram!")
    else:
        print("⚠️ Variáveis TELEGRAM não configuradas.")

def buscar_conteudo(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.text

def main():
    print("🚀 Monitoramento diário iniciado!")

    hash_atual = ""
    mensagens = []

    for url in URLS:
        try:
            html = buscar_conteudo(url)
            nova_hash = get_hash(html)

            # Lê hash antigo
            if os.path.exists(HASH_FILE):
                with open(HASH_FILE, "r") as f:
                    hash_antigo = f.read().strip()
            else:
                hash_antigo = ""

            if nova_hash != hash_antigo:
                mensagens.append(f"🧩 Mudança detectada em {url}")
                hash_atual = nova_hash  # atualiza hash

        except requests.HTTPError as e:
            mensagens.append(f"⚠️ Erro ao acessar {url}: {e}")

    # Atualiza hash
    if hash_atual:
        with open(HASH_FILE, "w") as f:
            f.write(hash_atual)

    # Envia notificações
    if mensagens:
        for msg in mensagens:
            enviar_telegram(msg)
    else:
        print("⏳ Nenhuma nova publicação encontrada.")

    print("✅ Monitoramento concluído!")

if __name__ == "__main__":
    main()
