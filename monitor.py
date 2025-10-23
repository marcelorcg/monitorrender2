import requests
import hashlib
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from telegram import Bot

# Carregar variáveis do .env
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
URL1 = os.getenv("URL1")
URL2 = os.getenv("URL2")

bot = Bot(token=TELEGRAM_TOKEN)

HASH_FILE = "hashes.json"

# Carregar hashes antigos
if os.path.exists(HASH_FILE):
    with open(HASH_FILE, "r") as f:
        hashes = json.load(f)
else:
    hashes = {}

def enviar_telegram(mensagem):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=mensagem)
    except Exception as e:
        print("Erro ao enviar Telegram:", e)

def obter_conteudo(url, ignore_ssl=False):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers, verify=not ignore_ssl, timeout=20)
        r.raise_for_status()
        return r.text
    except requests.exceptions.SSLError as e:
        if ignore_ssl:
            return None
        return f"Erro SSL: {e}"
    except requests.exceptions.HTTPError as e:
        return f"HTTP Error: {e}"
    except requests.exceptions.RequestException as e:
        return f"Erro de conexão: {e}"

def verificar_site(nome, url, hashes, ignore_ssl=False):
    conteudo = obter_conteudo(url, ignore_ssl)
    if conteudo is None or conteudo.startswith(("Erro", "HTTP Error")):
        enviar_telegram(f"⚠️ {nome} inacessível ({conteudo}), monitoramento ignorado hoje.")
        return hashes

    novo_hash = hashlib.sha256(conteudo.encode("utf-8")).hexdigest()
    if url not in hashes or hashes[url] != novo_hash:
        enviar_telegram(f"🚨 Mudança detectada em {nome}!\n{url}\n📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        hashes[url] = novo_hash
    return hashes

def main():
    enviar_telegram(
        "🚀 Iniciando monitoramento diário dos sites de concursos...\n\n"
        f"1️⃣ Câmara SJC: {URL1}\n2️⃣ Prefeitura Caçapava: {URL2}\n\n"
        f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
    )

    global hashes
    # Câmara SJC (ignora SSL)
    hashes = verificar_site("Câmara SJC", URL1, hashes, ignore_ssl=True)
    # Prefeitura Caçapava
    hashes = verificar_site("Prefeitura Caçapava", URL2, hashes)

    # Salvar hashes atualizados
    with open(HASH_FILE, "w") as f:
        json.dump(hashes, f, indent=2)

    enviar_telegram(f"✅ Monitoramento concluído!\n📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

if __name__ == "__main__":
    main()
