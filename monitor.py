#!/usr/bin/env python3
# monitor.py – versão final: monitor diário às 9h com função corrigida

import os
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

# ---- funções ----
def enviar_telegram(texto: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram não configurado. Mensagem não enviada.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": texto}
    try:
        resp = requests.post(url, data=data, timeout=10)
        if resp.status_code == 200:
            print("✅ Mensagem enviada no Telegram!")
        else:
            print(f"⚠️ Erro Telegram (HTTP {resp.status_code}): {resp.text}")
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

def obter_conteudo(url):
    """Retorna sempre (conteudo, via_fallback, erro)"""
    try:
        r = requests.get(url, headers=HEADERS, timeout=15, verify=False)
        r.raise_for_status()
        return r.text, False, None
    except requests.exceptions.RequestException:
        try:
            proxy_url = "https://r.jina.ai/http://" + url.replace("https://", "").replace("http://", "")
            r2 = requests.get(proxy_url, headers=HEADERS, timeout=15)
            r2.raise_for_status()
            return r2.text, True, None
        except Exception as e2:
            return None, False, str(e2)

def gerar_hash_texto(texto):
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()

def verificar_site(nome, url, hashes):
    tz = ZoneInfo("America/Sao_Paulo")
    agora = datetime.now(tz).strftime("%d/%m/%Y %H:%M:%S")
    print(f"⏳ Verificando {nome} ({url})...")
    conteudo, via_fallback, erro = obter_conteudo(url)
    if erro:
        msg = f"❌ Erro ao verificar {nome}: {erro}\n📅 {agora}"
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
        fonte = " (via fallback)" if via_fallback else ""
        msg = f"🧩 Primeiro monitoramento de {nome}{fonte} — hash salvo.\n📅 {agora}"
        print(msg)
        enviar_telegram(msg)
        return hashes

    if novo_hash != antigo_hash:
        hashes[url] = novo_hash
        salvar_hashes(hashes)
        fonte = " (via fallback)" if via_fallback else ""
        msg = f"🚨 Mudança detectada em {nome}{fonte}!\n{url}\n📅 {agora}"
        print(msg)
        enviar_telegram(msg)
    else:
        fonte = " (via fallback)" if via_fallback else ""
        msg = f"✅ {nome} não apresentou mudanças{fonte}.\n📅 {agora}"
        print(msg)

    return hashes

# ---- principal ----
def main():
    tz = ZoneInfo("America/Sao_Paulo")
    agora = datetime.now(tz).strftime("%d/%m/%Y %H:%M:%S")
    intro = (
        "🚀 Iniciando monitoramento diário dos sites de concursos...\n\n"
        f"1️⃣ Câmara SJC: {URL1}\n"
        f"2️⃣ Prefeitura Caçapava: {URL2}\n\n"
        f"📅 {agora}"
    )
    enviar_telegram(intro)

    hashes = carregar_hashes()
    hashes = verificar_site("Câmara SJC", URL1, hashes)
    hashes = verificar_site("Prefeitura Caçapava", URL2, hashes)

    finalizar = f"✅ Monitoramento concluído!\n📅 {agora}"
    enviar_telegram(finalizar)

if __name__ == "__main__":
    main()
