#!/usr/bin/env python3
# monitor_24h.py

import os
import time
import json
import hashlib
import requests
import difflib
from datetime import datetime
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import urllib3
import re

# ---- configuração ----
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
URL1 = os.getenv("URL1")
URL2 = os.getenv("URL2")

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("Defina TELEGRAM_TOKEN e TELEGRAM_CHAT_ID no .env")

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
        resp.raise_for_status()
        print("✅ Mensagem enviada no Telegram!")
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

def limpar_texto(texto):
    """Remove partes irrelevantes (cookies, rodapé, scripts)"""
    texto = re.sub(r"(?i)cookie.*|política de privacidade.*|rodapé.*", "", texto, flags=re.DOTALL)
    texto = re.sub(r"\s+", " ", texto)  # reduz múltiplos espaços
    return texto.strip()

def obter_conteudo_com_fallback(url, headers=None, timeout=10):
    headers = headers or HEADERS
    try:
        r = requests.get(url, headers=headers, timeout=timeout, verify=False)
        r.raise_for_status()
        return r.text, False, None
    except requests.exceptions.RequestException as e:
        # tenta fallback via r.jina.ai
        try:
            proxy_url = "https://r.jina.ai/http://" + url.replace("https://", "").replace("http://", "")
            r2 = requests.get(proxy_url, headers=headers, timeout=15)
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
    print(f"⏳ Verificando {nome} ({url})...")
    conteudo, via_fallback, erro = obter_conteudo_com_fallback(url)
    if erro:
        msg = f"⚠️ {nome}: não foi possível acessar ({url}). Motivo: {erro}\n📅 {agora}"
        print(msg)
        return hashes, msg

    soup = BeautifulSoup(conteudo, "html.parser")
    texto_visivel = limpar_texto(soup.get_text(separator="\n", strip=True))
    novo_hash = gerar_hash_texto(texto_visivel)

    antigo_hash = hashes.get(url)
    if antigo_hash is None:
        hashes[url] = novo_hash
        salvar_hashes(hashes)
        msg = f"🧩 Primeiro monitoramento de {nome}{' (via fallback)' if via_fallback else ''} ({url}) — hash salvo.\n📅 {agora}"
        print(msg)
        return hashes, msg

    if novo_hash != antigo_hash:
        hashes[url] = novo_hash
        salvar_hashes(hashes)
        msg = f"🚨 Mudança detectada em {nome}{' (via fallback)' if via_fallback else ''}!\n{url}\n📅 {agora}"
        print(msg)
        return hashes, msg

    # sem mudanças importantes
    print(f"✅ {nome} não apresentou mudanças{' (via fallback)' if via_fallback else ''}.")
    return hashes, None

# ---- loop principal 24h ----
def main():
    tz = ZoneInfo("America/Sao_Paulo")
    hashes = carregar_hashes()
    alerta_enviado_hoje = False

    while True:
        agora = datetime.now(tz)
        hora = agora.hour
        minuto = agora.minute

        # enviar alerta diário somente às 9h
        if hora == 9 and not alerta_enviado_hoje:
            intro = (
                "🚀 Monitoramento diário iniciado!\n\n"
                f"1️⃣ Câmara SJC: {URL1}\n"
                f"2️⃣ Prefeitura Caçapava: {URL2}\n\n"
                f"📅 {agora.strftime('%d/%m/%Y %H:%M:%S')}"
            )
            enviar_telegram(intro)

            hashes, msg1 = verificar_site("Câmara SJC", URL1, hashes)
            if msg1:
                enviar_telegram(msg1)

            hashes, msg2 = verificar_site("Prefeitura Caçapava", URL2, hashes)
            if msg2:
                enviar_telegram(msg2)

            finalizar = f"✅ Monitoramento concluído!\n📅 {agora.strftime('%d/%m/%Y %H:%M:%S')}"
            enviar_telegram(finalizar)
            alerta_enviado_hoje = True

        # reset diário do alerta
        if hora == 0 and minuto == 0:
            alerta_enviado_hoje = False

        # verifica cada 30 minutos mas não envia alerta fora do horário
        time.sleep(1800)

if __name__ == "__main__":
    main()
