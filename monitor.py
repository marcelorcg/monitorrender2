import os
import requests
from hashlib import sha256
from datetime import datetime
from dotenv import load_dotenv
from telegram import Bot
from bs4 import BeautifulSoup

# Carrega variáveis do .env
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
URLS = [
    "https://www.cacapava.sp.gov.br/publicacoes/concursos-publicos/concurso-publico-012024",
    "https://www.camarasjc.sp.gov.br/a-camara/concurso-publico.php"
]

HASH_FILE = "hashes.json"

import json

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
    r = requests.get(url, headers=headers, verify=False)  # Ignora SSL
    r.raise_for_status()
    return r.text

def main():
    print(f"🚀 Monitoramento iniciado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Lê hashes antigos
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r") as f:
            hash_antigos = json.load(f)
    else:
        hash_antigos = {}

    hash_novos = {}
    mensagens = []

    for url in URLS:
        try:
            html = buscar_conteudo(url)
            nova_hash = get_hash(html)
            hash_novos[url] = nova_hash

            if url not in hash_antigos or hash_antigos[url] != nova_hash:
                mensagens.append(f"🚨 Mudança detectada em {url}!\n📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            else:
                print(f"✅ Nenhuma mudança: {url}")

        except requests.HTTPError as e:
            mensagens.append(f"⚠️ Site inacessível: {url} ({e})")
        except Exception as e:
            mensagens.append(f"⚠️ Erro desconhecido: {url} ({e})")

    # Atualiza arquivo de hashes
    with open(HASH_FILE, "w") as f:
        json.dump(hash_novos, f, indent=4)

    # Envia notificações
    for msg in mensagens:
        enviar_telegram(msg)

    print(f"✅ Monitoramento concluído em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

if __name__ == "__main__":
    main()
