# monitor.py
import os
import json
import hashlib
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from telegram import Bot
from requests.exceptions import RequestException, HTTPError, SSLError

# Carregar variáveis do .env
from dotenv import load_dotenv
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
URL1 = os.getenv("URL1")
URL2 = os.getenv("URL2")

bot = Bot(token=TELEGRAM_TOKEN)
HASH_FILE = "hashes.json"

def carregar_hashes():
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_hashes(hashes):
    with open(HASH_FILE, "w", encoding="utf-8") as f:
        json.dump(hashes, f, indent=2)

def obter_conteudo(url):
    try:
        r = requests.get(url, timeout=20, verify=False)  # SSL ignorado para evitar erro de certificado
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        return soup.get_text(separator="\n", strip=True)
    except HTTPError as he:
        return None, f"HTTP Error: {he}"
    except SSLError as se:
        return None, f"SSL Error: {se}"
    except RequestException as e:
        return None, f"Request Error: {e}"

def hash_conteudo(conteudo):
    return hashlib.sha256(conteudo.encode("utf-8")).hexdigest()

def verificar_site(nome, url, hashes):
    conteudo, erro = obter_conteudo(url) if True else (None, None)
    if conteudo is None:
        return hashes, f"⚠️ {nome} inacessível ({erro}), monitoramento ignorado hoje."
    h = hash_conteudo(conteudo)
    if url not in hashes or hashes[url] != h:
        hashes[url] = h
        salvar_hashes(hashes)
        bot.send_message(chat_id=TELEGRAM_CHAT_ID,
                         text=f"🚨 Mudança detectada em {nome}! {url}\n📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    return hashes, None

def main():
    bot.send_message(chat_id=TELEGRAM_CHAT_ID,
                     text=f"🚀 Iniciando monitoramento diário dos sites de concursos...\n\n1️⃣ Câmara SJC: {URL1}\n2️⃣ Prefeitura Caçapava: {URL2}\n📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    hashes = carregar_hashes()

    hashes, msg1 = verificar_site("Câmara SJC", URL1, hashes)
    if msg1:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg1)

    hashes, msg2 = verificar_site("Prefeitura Caçapava", URL2, hashes)
    if msg2:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg2)

    bot.send_message(chat_id=TELEGRAM_CHAT_ID,
                     text=f"✅ Monitoramento concluído!\n📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

if __name__ == "__main__":
    main()
