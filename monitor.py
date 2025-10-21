#!/usr/bin/env python3
# monitor.py
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

def obter_conteudo_com_fallback(url, headers=None, timeout=10):
    """
    Tenta obter o HTML/texto do site:
    1) Requisição direta com headers (verify=False para evitar bloqueio de certificado).
    2) Se der 403 ou falha que pareça bloqueio, tenta fallback via r.jina.ai (text proxy).
    Retorna (conteudo_texto, via_fallback_bool, erro_mensagem_or_None)
    """
    headers = headers or HEADERS
    try:
        r = requests.get(url, headers=headers, timeout=timeout, verify=False)
        r.raise_for_status()
        return r.text, False, None
    except requests.exceptions.HTTPError as he:
        status = getattr(he.response, "status_code", None)
        # se for 403 ou similar, tenta fallback
        if status == 403:
            # tenta fallback
            try:
                proxy_url = "https://r.jina.ai/http://" + url.replace("https://", "").replace("http://", "")
                r2 = requests.get(proxy_url, headers=headers, timeout=15)
                r2.raise_for_status()
                return r2.text, True, None
            except Exception as e2:
                return None, False, f"HTTP 403 e fallback falhou: {e2}"
        else:
            return None, False, f"HTTPError: {he}"
    except requests.exceptions.RequestException as re:
        # tentamos fallback em caso de erro de rede/403 repetido
        try:
            proxy_url = "https://r.jina.ai/http://" + url.replace("https://", "").replace("http://", "")
            r2 = requests.get(proxy_url, headers=headers, timeout=15)
            r2.raise_for_status()
            return r2.text, True, None
        except Exception as e2:
            return None, False, f"RequestException: {re} | fallback falhou: {e2}"

def gerar_hash_texto(texto):
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()

# ---- monitoramento ----
def verificar_site(nome, url, hashes):
    tz = ZoneInfo("America/Sao_Paulo")
    agora = datetime.now(tz).strftime("%d/%m/%Y %H:%M:%S")
    print(f"⏳ Verificando {nome} ({url})...")
    conteudo, via_fallback, erro = obter_conteudo_com_fallback(url)
    if erro:
        # se erro que não conseguimos recuperar, não enviar alerta 403 repetido — apenas informa no telegram/console
        msg = f"⚠️ {nome}: não foi possível acessar ({url}). Motivo: {erro}\n📅 {agora}"
        print(msg)
        enviar_telegram(msg)
        return hashes  # sem alterações
    # extrair texto limpo
    soup = BeautifulSoup(conteudo, "html.parser")
    texto_visivel = soup.get_text(separator="\n", strip=True)
    novo_hash = gerar_hash_texto(texto_visivel)

    antigo_hash = hashes.get(url)
    if antigo_hash is None:
        hashes[url] = novo_hash
        salvar_hashes(hashes)
        fonte = " (via fallback)" if via_fallback else ""
        msg = f"🧩 Primeiro monitoramento de {nome}{fonte} ({url}) — hash salvo.\n📅 {agora}"
        print(msg)
        enviar_telegram(msg)
        return hashes

    if novo_hash != antigo_hash:
        # gera diff simples (linhas novas)
        diff = list(difflib.unified_diff(
            antigo_hash.splitlines(),
            novo_hash.splitlines(),
            lineterm=""
        ))
        # enviamos notificação curta com link
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
        # (opcional) não enviar no Telegram a cada execução para economizar mensagens
        # enviar_telegram(msg)
    return hashes

def main():
    tz = ZoneInfo("America/Sao_Paulo")
    agora = datetime.now(tz).strftime("%d/%m/%Y %H:%M:%S")
    # mensagem inicial resumida
    intro = (
        "🚀 Monitoramento diário iniciado!\n\n"
        "Sites verificados:\n"
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
