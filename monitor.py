#!/usr/bin/env python3
# monitor.py
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

# ---- utilitários ----
def enviar_telegram(texto: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram não configurado corretamente.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": texto}
    try:
        requests.post(url, data=data, timeout=10)
        print("✅ Mensagem enviada no Telegram!")
    except Exception as e:
        print(f"⚠️ Falha ao enviar Telegram: {e}")

def carregar_hashes():
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_hashes(hashes):
    with open(HASH_FILE, "w", encoding="utf-8") as f:
        json.dump(hashes, f, ensure_ascii=False, indent=2)

def obter_conteudo_com_fallback(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10, verify=False)
        r.raise_for_status()
        return r.text, False, None
    except requests.exceptions.HTTPError as he:
        status = getattr(he.response, "status_code", None)
        if status == 403:
            try:
                proxy_url = "https://r.jina.ai/http://" + url.replace("https://", "")
                r2 = requests.get(proxy_url, headers=HEADERS, timeout=15)
                r2.raise_for_status()
                return r2.text, True, None
            except Exception as e2:
                return None, False, f"HTTP 403 e fallback falhou: {e2}"
        return None, False, f"HTTPError: {he}"
    except Exception as e:
        return None, False, str(e)

def gerar_hash_texto(texto):
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()

# ---- verificação ----
def verificar_site(nome, url, hashes):
    tz = ZoneInfo("America/Sao_Paulo")
    agora = datetime.now(tz).strftime("%d/%m/%Y %H:%M:%S")
    print(f"🌐 Verificando {nome} → {url}")
    conteudo, via_fallback, erro = obter_conteudo_com_fallback(url)
    if erro or not conteudo:
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
        msg = f"📘 Primeiro monitoramento de {nome} realizado com sucesso!"
        print(msg)
        enviar_telegram(msg)
        return hashes

    if novo_hash != antigo_hash:
        hashes[url] = novo_hash
        salvar_hashes(hashes)
        msg = f"🚨 Mudança detectada em {nome}! {url}\n📅 {agora}"
        print(msg)
        enviar_telegram(msg)
    else:
        msg = f"✅ {nome} sem mudanças relevantes.\n📅 {agora}"
        print(msg)
        enviar_telegram(msg)
    return hashes

# ---- principal ----
def main():
    tz = ZoneInfo("America/Sao_Paulo")
    agora = datetime.now(tz).strftime("%d/%m/%Y %H:%M:%S")
    print("🚀 Iniciando monitoramento diário dos sites de concursos...\n")

    intro = (
        f"🚀 Iniciando monitoramento diário dos sites de concursos...\n\n"
        f"1️⃣ Câmara SJC: {URL1}\n"
        f"2️⃣ Prefeitura Caçapava: {URL2}\n\n"
        f"📅 {agora}"
    )
    enviar_telegram(intro)

    hashes = carregar_hashes()
    hashes = verificar_site("Câmara SJC", URL1, hashes)
    hashes = verificar_site("Prefeitura de Caçapava", URL2, hashes)

    salvar_hashes(hashes)
    print("💾 Hashes atualizados e salvos localmente.")
    enviar_telegram("✅ Monitoramento concluído!\n📅 " + agora)

if __name__ == "__main__":
    main()
