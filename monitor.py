import os
import requests
from bs4 import BeautifulSoup
from hashlib import sha256
from datetime import datetime
from time import sleep
from dotenv import load_dotenv
from telegram import Bot
import json

# 🧭 Carrega variáveis de ambiente
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 🔹 Verifica variáveis
if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    print("⚠️ Problema com variáveis do .env:")
    if not TELEGRAM_TOKEN:
        print("   ❌ TELEGRAM_TOKEN não encontrado ou vazio.")
    if not TELEGRAM_CHAT_ID:
        print("   ❌ TELEGRAM_CHAT_ID não encontrado ou vazio.")
    exit(1)

# 🔹 Inicializa bot do Telegram
bot = Bot(token=TELEGRAM_TOKEN)

# 🔹 Arquivos do projeto
HASH_FILE = "hashes.json"
SITES_FILE = "sites.txt"

# 🕓 Função para horário local (Brasil)
def agora():
    import pytz
    tz = pytz.timezone("America/Sao_Paulo")
    return datetime.now(tz).strftime("%d/%m/%Y %H:%M:%S")

# 💾 Lê e grava hashes
def carregar_hashes():
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_hashes(hashes):
    with open(HASH_FILE, "w", encoding="utf-8") as f:
        json.dump(hashes, f, indent=2, ensure_ascii=False)

# 📩 Envia mensagem ao Telegram
def enviar(msg):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)
        print(f"✅ Telegram: {msg}")
    except Exception as e:
        print(f"⚠️ Erro ao enviar Telegram: {e}")

# 🔍 Lê sites do sites.txt
def carregar_sites():
    if not os.path.exists(SITES_FILE):
        print(f"⚠️ {SITES_FILE} não encontrado. Crie o arquivo com os sites, 1 por linha.")
        exit(1)
    with open(SITES_FILE, "r", encoding="utf-8") as f:
        return [linha.strip() for linha in f if linha.strip()]

# 🌐 Busca conteúdo do site (SSL ignorado e user-agent humanizado)
def buscar_conteudo(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0",
        "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }
    try:
        r = requests.get(url, headers=headers, timeout=20, verify=False)
        r.raise_for_status()
        return r.text, None
    except requests.exceptions.RequestException as e:
        return None, str(e)

# 🔐 Gera hash do conteúdo
def gerar_hash(conteudo):
    return sha256(conteudo.encode("utf-8")).hexdigest()

# 🧠 Verifica mudanças no site
def verificar_site(url, hashes):
    conteudo, erro = buscar_conteudo(url)
    if erro:
        enviar(f"⚠️ Site inacessível: {url} ({erro})")
        return hashes
    hash_atual = gerar_hash(conteudo)
    if url not in hashes:
        hashes[url] = hash_atual
    elif hash_atual != hashes[url]:
        enviar(f"🚨 Mudança detectada em {url}!\n📅 {agora()}")
        hashes[url] = hash_atual
    return hashes

# 🚀 Função principal
def main():
    print(f"🚀 Monitoramento iniciado em {agora()}")

    sites = carregar_sites()
    hashes = carregar_hashes()

    # 🔹 Modo síncrono: verifica site por site, com delay
    for url in sites:
        hashes = verificar_site(url, hashes)
        sleep(3)  # ⏳ delay de 3 segundos entre sites para parecer humano

    salvar_hashes(hashes)
    print(f"✅ Monitoramento concluído em {agora()}")

if __name__ == "__main__":
    main()
