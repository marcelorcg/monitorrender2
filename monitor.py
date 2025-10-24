import os
import hashlib
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from telegram import Bot
from datetime import datetime
import pytz
import json

# 🧭 Carrega variáveis de ambiente
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
URL1 = os.getenv("URL1")
URL2 = os.getenv("URL2")

bot = Bot(token=TELEGRAM_TOKEN)
HASH_FILE = "hashes.json"

# 🕓 Função para horário local (Brasil)
def agora():
    tz = pytz.timezone("America/Sao_Paulo")
    return datetime.now(tz).strftime("%d/%m/%Y %H:%M:%S")

# 📩 Envia mensagem ao Telegram
def enviar(msg):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

# 💾 Lê e grava hashes (para lembrar estado anterior)
def carregar_hashes():
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_hashes(hashes):
    with open(HASH_FILE, "w", encoding="utf-8") as f:
        json.dump(hashes, f, indent=2, ensure_ascii=False)

# 🌐 Obtém conteúdo HTML (com cabeçalho de navegador)
def obter_conteudo(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/119.0 Safari/537.36"
        ),
        "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    }

    try:
        resp = requests.get(url, timeout=20, verify=True, headers=headers)
        resp.raise_for_status()
        return resp.text, None
    except requests.exceptions.SSLError:
        resp = requests.get(url, timeout=20, verify=False, headers=headers)
        resp.raise_for_status()
        return resp.text, None
    except requests.exceptions.RequestException as e:
        return None, str(e)

# 🔍 Gera hash do conteúdo textual
def gerar_hash(conteudo):
    return hashlib.sha256(conteudo.encode("utf-8")).hexdigest()

# 🧠 Verifica se o site mudou
def verificar_site(nome, url, hashes):
    conteudo, erro = obter_conteudo(url)

    if erro:
        enviar(f"⚠️ {nome} inacessível ({erro}), monitoramento ignorado hoje.")
        return hashes

    soup = BeautifulSoup(conteudo, "html.parser")
    texto = soup.get_text()
    hash_atual = gerar_hash(texto)

    if url not in hashes:
        hashes[url] = hash_atual
    elif hash_atual != hashes[url]:
        enviar(f"🚨 Mudança detectada em {nome}!\n{url}\n📅 {agora()}")
        hashes[url] = hash_atual

    return hashes

# 🚀 Função principal
def main():
    enviar(f"🤖 Monitor ativo e pronto — sem erros SSL.\n🚀 Iniciando monitoramento diário dos sites de concursos...\n\n"
           f"1️⃣ Câmara SJC: {URL1}\n2️⃣ Prefeitura Caçapava: {URL2}\n\n📅 {agora()}")

    hashes = carregar_hashes()
    hashes = verificar_site("Câmara SJC", URL1, hashes)
    hashes = verificar_site("Prefeitura Caçapava", URL2, hashes)
    salvar_hashes(hashes)

    enviar(f"✅ Monitoramento concluído!\n📅 {agora()}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        enviar(f"💥 Erro inesperado: {e}\n📅 {agora()}")
        print(f"Erro: {e}")
