#!/usr/bin/env python3
# monitor.py
import os
import time
import json
import hashlib
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import urllib3

# ---- configuração ----
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
URL1 = os.getenv("URL1")
URL2 = os.getenv("URL2")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "pt-BR,pt;q=0.9",
}

HASH_FILE = "hashes.json"

# ---- funções utilitárias ----
def enviar_telegram(texto: str):
    """Envia mensagem ao Telegram"""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram não configurado corretamente.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": texto}
    try:
        resp = requests.post(url, data=data, timeout=10)
        if resp.status_code == 200:
            print("✅ Mensagem enviada ao Telegram.")
        else:
            print(f"⚠️ Erro HTTP {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"⚠️ Erro ao enviar mensagem: {e}")

def carregar_hashes():
    if os.path.exists(HASH_FILE):
        try:
            with open(HASH_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def salvar_hashes(hashes):
    with open(HASH_FILE, "w", encoding="utf-8") as f:
        json.dump(hashes, f, ensure_ascii=False, indent=2)

def gerar_hash(texto):
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()

def obter_conteudo(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=20, verify=False)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"⚠️ Falha ao acessar {url}: {e}")
        return None

def verificar_site(nome, url, hashes):
    tz = ZoneInfo("America/Sao_Paulo")
    agora = datetime.now(tz).strftime("%d/%m/%Y %H:%M:%S")

    print(f"⏳ Verificando {nome} ({url})...")
    conteudo = obter_conteudo(url)
    if not conteudo:
        msg = f"⚠️ Não foi possível acessar {nome}.\n📅 {agora}"
        enviar_telegram(msg)
        return hashes

    soup = BeautifulSoup(conteudo, "html.parser")
    texto = soup.get_text(separator="\n", strip=True)
    novo_hash = gerar_hash(texto)

    antigo_hash = hashes.get(url)
    if antigo_hash is None:
        hashes[url] = novo_hash
        salvar_hashes(hashes)
        enviar_telegram(f"🧩 Primeiro monitoramento de {nome}.\n📅 {agora}")
        return hashes

    if novo_hash != antigo_hash:
        hashes[url] = novo_hash
        salvar_hashes(hashes)
        msg = f"🚨 Mudança detectada em {nome}!\n{url}\n📅 {agora}"
        enviar_telegram(msg)
    else:
        print(f"✅ {nome} sem mudanças ({agora})")
    return hashes

# ---- função principal ----
def main():
    tz = ZoneInfo("America/Sao_Paulo")
    hashes = carregar_hashes()

    while True:
        agora = datetime.now(tz)
        hora_atual = agora.strftime("%H:%M")

        if hora_atual == "09:00":
            intro = (
                "🚀 Monitoramento diário iniciado!\n\n"
                f"1️⃣ Câmara SJC: {URL1}\n"
                f"2️⃣ Prefeitura Caçapava: {URL2}\n\n"
                f"📅 {agora.strftime('%d/%m/%Y %H:%M:%S')}"
            )
            enviar_telegram(intro)
            hashes = verificar_site("Câmara SJC", URL1, hashes)
            hashes = verificar_site("Prefeitura Caçapava", URL2, hashes)
            enviar_telegram("✅ Monitoramento concluído!\n📅 " + agora.strftime("%d/%m/%Y %H:%M:%S"))

            # Espera até o próximo dia (24 horas)
            print("😴 Aguardando 24 horas até a próxima checagem...")
            time.sleep(24 * 60 * 60)

        else:
            # Dorme por 60 segundos e volta a checar se é 9h
            time.sleep(60)

if __name__ == "__main__":
    main()
