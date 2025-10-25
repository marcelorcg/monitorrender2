#!/usr/bin/env python3
# monitor.py - versão robusta para Railway
import requests
import hashlib
import json
import os
from datetime import datetime
from time import sleep

from requests.adapters import HTTPAdapter, Retry
from urllib3.exceptions import InsecureRequestWarning
import urllib3
urllib3.disable_warnings(InsecureRequestWarning)  # Ignora warnings SSL

from telegram import Bot
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    print("⚠️ Variáveis TELEGRAM não configuradas.")
    exit(1)

bot = Bot(token=TELEGRAM_TOKEN)

# Arquivos de configuração
SITES_FILE = "sites.txt"
HASHES_FILE = "hashes.json"

# Headers para simular browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

# Função para carregar sites do sites.txt
def carregar_sites():
    if os.path.exists(SITES_FILE):
        with open(SITES_FILE, "r") as f:
            sites = [linha.strip() for linha in f if linha.strip()]
        return sites
    return []

# Função para carregar hashes anteriores
def carregar_hashes():
    if os.path.exists(HASHES_FILE):
        with open(HASHES_FILE, "r") as f:
            return json.load(f)
    return {}

# Função para salvar hashes
def salvar_hashes(hashes):
    with open(HASHES_FILE, "w") as f:
        json.dump(hashes, f, indent=4)

# Função para buscar conteúdo com retries
def buscar_conteudo(url):
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=2, status_forcelist=[403, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    try:
        r = session.get(url, headers=HEADERS, timeout=15, verify=False)
        r.raise_for_status()
        return r.text
    except requests.exceptions.HTTPError as e:
        return f"⚠️ HTTP Error: {e}"
    except requests.exceptions.RequestException as e:
        return f"⚠️ Request failed: {e}"

# Função principal
def main():
    print(f"🚀 Monitoramento iniciado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    sites = carregar_sites()
    hashes = carregar_hashes()
    novos_hashes = hashes.copy()

    for url in sites:
        print(f"🌐 Acessando {url}")
        conteudo = buscar_conteudo(url)
        hash_atual = hashlib.sha256(conteudo.encode("utf-8")).hexdigest() if not conteudo.startswith("⚠️") else None

        if hash_atual and url in hashes and hashes[url] != hash_atual:
            mensagem = f"🚨 Mudança detectada em {url}!\n{conteudo[:500]}..."
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=mensagem)
            print(f"✅ Telegram: {mensagem}")
        elif hash_atual and url not in hashes:
            # Primeira execução
            novos_hashes[url] = hash_atual
            print(f"✅ Primeiro monitoramento: {url}")
        elif not hash_atual:
            # Site inacessível, reporta no Telegram
            mensagem = f"⚠️ Site inacessível: {url}\n{conteudo}"
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=mensagem)
            print(f"✅ Telegram: {mensagem}")
        # Atualiza hash atual
        if hash_atual:
            novos_hashes[url] = hash_atual

    salvar_hashes(novos_hashes)
    print(f"✅ Monitoramento concluído em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

if __name__ == "__main__":
    main()
