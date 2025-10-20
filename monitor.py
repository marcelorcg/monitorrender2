import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv

# 🔹 Carrega variáveis do .env
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
URLS = [
    os.getenv("URL1"),
    os.getenv("URL2")
]

HASH_FILE = "hashes.json"

def enviar_telegram(mensagem):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Variáveis TELEGRAM não configuradas.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensagem}
    try:
        r = requests.post(url, data=payload)
        if r.status_code == 200:
            print("✅ Mensagem enviada no Telegram!")
        else:
            print(f"⚠️ Erro ao enviar mensagem: {r.status_code}")
    except Exception as e:
        print(f"⚠️ Erro ao enviar mensagem: {e}")

def obter_conteudo(url):
    try:
        r = requests.get(url)
        r.raise_for_status()
        return r.text
    except requests.HTTPError as e:
        print(f"⚠️ HTTP Error ao acessar {url}: {e}")
        return None
    except Exception as e:
        print(f"⚠️ Erro ao acessar {url}: {e}")
        return None

def carregar_hashes():
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_hashes(hashes):
    with open(HASH_FILE, "w", encoding="utf-8") as f:
        json.dump(hashes, f, ensure_ascii=False, indent=2)

def main():
    print("🚀 Monitoramento diário iniciado!")
    hashes = carregar_hashes()
    mudou = False

    for url in URLS:
        print(f"⏳ Verificando {url}...")
        conteudo = obter_conteudo(url)
        if conteudo is None:
            continue
        hash_atual = conteudo.strip()[:1000]  # simplificação do "hash"
        hash_antigo = hashes.get(url, "")
        if hash_atual != hash_antigo:
            print(f"🧩 Mudança detectada em {url} (hash atualizado).")
            enviar_telegram(f"🆕 Alteração detectada: {url}")
            hashes[url] = hash_atual
            mudou = True
        else:
            print(f"⏳ Nenhuma mudança em {url}.")

    salvar_hashes(hashes)
    print("✅ Monitoramento concluído!")

if __name__ == "__main__":
    main()
