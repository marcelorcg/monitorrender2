#!/usr/bin/env python3
# monitor.py
import os
import time
import json
import hashlib
import requests
from datetime import datetime
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

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("As variáveis TELEGRAM_TOKEN e TELEGRAM_CHAT_ID devem estar definidas no .env")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/128.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9",
    "Referer": "https://www.google.com/",
}

HASH_FILE = "hashes.json"

# ---- utilitários ----
def enviar_telegram(texto: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": texto}
    try:
        resp = requests.post(url, data=data, timeout=10)
        if resp.status_code == 200:
            print("✅ Mensagem enviada no Telegram!")
        else:
            print(f"⚠️ Erro HTTP ao enviar mensagem: {resp.status_code}")
    except Exception as e:
        print(f"⚠️ Erro ao enviar Telegram: {e}")

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

def obter_conteudo_com_fallback(url):
    """
    Requisição do site com fallback para evitar bloqueio 403 e SSL
    """
    try:
        r = requests.get(url, headers=HEADERS, timeout=10, verify=False)
        r.raise_for_status()
        return r.text, False, None
    except requests.exceptions.RequestException as e:
        # fallback via r.jina.ai
        try:
            proxy_url = "https://r.jina.ai/http://" + url.replace("https://", "").replace("http://", "")
            r2 = requests.get(proxy_url, headers=HEADERS, timeout=15)
            r2.raise_for_status()
            return r2.text, True, None
        except Exception as e2:
            return None, False, f"{e} | fallback falhou: {e2}"

def gerar_hash_texto(texto):
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()

# ---- monitoramento ----
def verificar_site(nome, url, hashes):
    tz = ZoneInfo("America/Sao_Paulo")
    agora = datetime.now(tz).strftime("%d/%m/%Y %H:%M:%S")
    print(f"🌐 Verificando {nome} → {url}")
    conteudo, via_fallback, erro = obter_conteudo_com_fallback(url)
    if erro:
        msg = f"❌ Erro ao verificar {nome}: {erro}"
        print(msg)
        enviar_telegram(msg)
        return hashes

    soup = BeautifulSoup(conteudo, "html.parser")
    texto_visivel = soup.get_text(separator="\n", strip=True)
    novo_hash = gerar_hash_texto(texto_visivel)

    antigo_hash = hashes.get(url)
    if antigo_hash is None:
        hashes[url] = novo_hash
        salvar_hashes(hashes)
        msg = f"🧩 Primeiro monitoramento de {nome}{' (via fallback)' if via_fallback else ''} — hash salvo."
        print(msg)
        enviar_telegram(msg)
        return hashes

    if novo_hash != antigo_hash:
        hashes[url] = novo_hash
        salvar_hashes(hashes)
        msg = f"🚨 Mudança detectada em {nome}{' (via fallback)' if via_fallback else ''}!"
        print(msg)
        enviar_telegram(msg)
    else:
        msg = f"✅ {nome} não apresentou mudanças{' (via fallback)' if via_fallback else ''}."
        print(msg)
    return hashes

# ---- loop diário ----
def main():
    tz = ZoneInfo("America/Sao_Paulo")
    while True:
        agora = datetime.now(tz)
        # enviar alerta inicial às 9h
        if agora.hour == 9 and agora.minute == 0:
            intro = (
                "🚀 Iniciando monitoramento diário dos sites de concursos...\n\n"
                f"1️⃣ Câmara SJC: {URL1}\n"
                f"2️⃣ Prefeitura Caçapava: {URL2}\n"
                f"📅 {agora.strftime('%d/%m/%Y %H:%M:%S')}"
            )
            enviar_telegram(intro)

            hashes = carregar_hashes()
            hashes = verificar_site("Câmara SJC", URL1, hashes)
            hashes = verificar_site("Prefeitura Caçapava", URL2, hashes)
            finalizar = f"✅ Monitoramento diário concluído!\n📅 {agora.strftime('%d/%m/%Y %H:%M:%S')}"
            enviar_telegram(finalizar)
            # espera 61 segundos para não enviar novamente no mesmo minuto
            time.sleep(61)
        # espera 30 segundos até checar novamente o horário
        time.sleep(30)

if __name__ == "__main__":
    main()
