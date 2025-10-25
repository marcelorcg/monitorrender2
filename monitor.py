import os
import requests
from bs4 import BeautifulSoup
from hashlib import sha256
from datetime import datetime
from time import sleep
from dotenv import load_dotenv
from telegram import Bot
import json
from urllib.parse import urlparse, urlunparse

# 🧭 Carrega variáveis do .env ou Railway
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=BOT_TOKEN) if BOT_TOKEN and CHAT_ID else None

# Arquivos
HASH_FILE = "hashes.json"
SITES_FILE = "sites.txt"

# ⏰ Função de horário Brasil
def agora():
    from pytz import timezone
    from datetime import datetime
    tz = timezone("America/Sao_Paulo")
    return datetime.now(tz).strftime("%d/%m/%Y %H:%M:%S")

# 🧩 Gera hash do conteúdo
def get_hash(content: str) -> str:
    return sha256(content.encode("utf-8")).hexdigest()

# 📩 Envia mensagem ao Telegram
def enviar_telegram(mensagem: str):
    if bot:
        bot.send_message(chat_id=CHAT_ID, text=mensagem)
        print("✅ Mensagem enviada no Telegram!")
    else:
        print("⚠️ Variáveis TELEGRAM não configuradas.")

# 🌐 Função humanizada para obter conteúdo
def buscar_conteudo(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive"
    }
    session = requests.Session()
    # Referer raiz
    parsed = urlparse(url)
    root = urlunparse((parsed.scheme, parsed.netloc, "/", "", "", ""))
    headers["Referer"] = root

    # Tentativa principal
    try:
        resp = session.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
        return resp.text
    except requests.HTTPError as e:
        if e.response.status_code == 403:
            # 🕓 Pausa e tenta novamente
            sleep(1.2)
            session.get(root, headers=headers, timeout=15)  # pega cookies
            sleep(0.5)
            resp2 = session.get(url, headers=headers, timeout=20)
            resp2.raise_for_status()
            return resp2.text
        else:
            raise
    except requests.RequestException as e:
        raise

# 💾 Carrega hashes existentes
def carregar_hashes():
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# 💾 Salva hashes atualizados
def salvar_hashes(hashes):
    with open(HASH_FILE, "w", encoding="utf-8") as f:
        json.dump(hashes, f, indent=2, ensure_ascii=False)

# 📄 Carrega sites do arquivo sites.txt
def carregar_sites():
    if not os.path.exists(SITES_FILE):
        enviar_telegram("⚠️ Nenhum arquivo sites.txt encontrado!")
        return []
    with open(SITES_FILE, "r", encoding="utf-8") as f:
        return [linha.strip() for linha in f.readlines() if linha.strip()]

# 🚀 Função principal
def main():
    sites = carregar_sites()
    if not sites:
        return

    lista_sites = "\n".join([f"{i+1}️⃣ {url}" for i, url in enumerate(sites)])
    enviar_telegram(f"🤖 Monitor ativo e pronto — sem erros SSL.\n🚀 Iniciando monitoramento diário...\n\n{lista_sites}\n\n📅 {agora()}")

    hashes = carregar_hashes()
    atualizou_hash = False

    for i, url in enumerate(sites):
        nome_site = f"Site {i+1}"
        try:
            html = buscar_conteudo(url)
            nova_hash = get_hash(html)

            if url not in hashes or hashes[url] != nova_hash:
                enviar_telegram(f"🧩 Mudança detectada em {nome_site}\n{url}\n📅 {agora()}")
                hashes[url] = nova_hash
                atualizou_hash = True

            sleep(0.8)  # pausa humanizada entre sites

        except Exception as e:
            enviar_telegram(f"⚠️ {nome_site} inacessível ({e}), monitoramento ignorado hoje.")

    if atualizou_hash:
        salvar_hashes(hashes)

    enviar_telegram(f"✅ Monitoramento concluído!\n📅 {agora()}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        enviar_telegram(f"💥 Erro inesperado: {e}\n📅 {agora()}")
        print(f"Erro: {e}")
