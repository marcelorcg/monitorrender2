import os
import hashlib
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from telegram import Bot
from datetime import datetime
import pytz
import urllib3

# 🧩 Desativa aviso de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 🧭 Carrega variáveis de ambiente
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
URL1 = os.getenv("URL1")
URL2 = os.getenv("URL2")

bot = Bot(token=TELEGRAM_TOKEN)

# 🕓 Retorna horário atual no Brasil
def agora():
    tz = pytz.timezone("America/Sao_Paulo")
    return datetime.now(tz).strftime("%d/%m/%Y %H:%M:%S")

# 📩 Envia mensagem ao Telegram
def enviar(msg):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

# 🌐 Obtém o conteúdo HTML do site (modo síncrono estável)
def obter_conteudo(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.google.com/",
        "Connection": "close"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=30, verify=False)
        if resp.status_code == 403:
            return None, "bloqueado (403 Forbidden)"
        resp.raise_for_status()
        return resp.text, None
    except Exception as e:
        return None, str(e)

# 🔍 Gera hash do conteúdo
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

    if nome not in hashes:
        hashes[nome] = hash_atual
    elif hash_atual != hashes[nome]:
        enviar(f"🚨 Mudança detectada em {nome}!\n{url}\n📅 {agora()}")
        hashes[nome] = hash_atual

    return hashes

# 🚀 Função principal
def main():
    enviar(
        f"🤖 Monitor ativo e pronto — sem erros SSL.\n"
        f"🚀 Iniciando monitoramento diário dos sites de concursos...\n\n"
        f"1️⃣ Câmara SJC: {URL1}\n"
        f"2️⃣ Prefeitura Caçapava: {URL2}\n\n"
        f"📅 {agora()}"
    )

    hashes = {}
    hashes = verificar_site("Câmara SJC", URL1, hashes)
    hashes = verificar_site("Prefeitura Caçapava", URL2, hashes)

    enviar(f"✅ Monitoramento concluído!\n📅 {agora()}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        enviar(f"💥 Erro inesperado: {e}\n📅 {agora()}")
        print(f"Erro: {e}")
