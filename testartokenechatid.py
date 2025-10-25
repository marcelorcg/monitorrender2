import os
import requests
from bs4 import BeautifulSoup
from hashlib import sha256
from datetime import datetime
from dotenv import load_dotenv
from telegram import Bot

# 🧭 Carrega variáveis de ambiente
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Checagem detalhada das variáveis do .env
if not BOT_TOKEN or not CHAT_ID:
    print("⚠️ Problema com variáveis do .env:")
    if not BOT_TOKEN:
        print("   ❌ TELEGRAM_TOKEN não encontrado ou vazio.")
    if not CHAT_ID:
        print("   ❌ TELEGRAM_CHAT_ID não encontrado ou vazio.")
    print("🔹 Certifique-se de que o arquivo .env está na mesma pasta que monitor.py")
    print("🔹 As variáveis devem estar sem aspas ou espaços extras")
    exit(1)  # Encerra o script se faltar alguma variável

# Inicializa bot do Telegram
bot = Bot(token=BOT_TOKEN)

# Lista de URLs de teste (ou ler de sites.txt se preferir)
URLS = [
    "https://www.cacapava.sp.gov.br/publicacoes",
    "https://www.camarasjc.sp.gov.br/a-camara/concurso-publico.php"
]

HASH_FILE = "hashes.json"

import json

def get_hash(content: str) -> str:
    return sha256(content.encode("utf-8")).hexdigest()

def enviar_telegram(mensagem: str):
    try:
        bot.send_message(chat_id=CHAT_ID, text=mensagem)
        print("✅ Mensagem enviada no Telegram!")
    except Exception as e:
        print(f"⚠️ Erro ao enviar mensagem: {e}")

def carregar_hashes():
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_hashes(hashes):
    with open(HASH_FILE, "w", encoding="utf-8") as f:
        json.dump(hashes, f, indent=2, ensure_ascii=False)

def buscar_conteudo(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    r = requests.get(url, headers=headers, verify=False)
    r.raise_for_status()
    return r.text

def main():
    print("🚀 Monitoramento diário iniciado!")

    hashes = carregar_hashes()
    mensagens = []

    for url in URLS:
        try:
            html = buscar_conteudo(url)
            nova_hash = get_hash(html)

            if url not in hashes or hashes[url] != nova_hash:
                mensagens.append(f"🧩 Mudança detectada em {url}")
                hashes[url] = nova_hash

        except requests.HTTPError as e:
            mensagens.append(f"⚠️ Erro ao acessar {url}: {e}")

    salvar_hashes(hashes)

    if mensagens:
        for msg in mensagens:
            enviar_telegram(msg)
    else:
        print("⏳ Nenhuma nova publicação encontrada.")

    print("✅ Monitoramento concluído!")

if __name__ == "__main__":
    main()
