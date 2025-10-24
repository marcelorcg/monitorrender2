import os
import hashlib
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from telegram import Bot
from datetime import datetime
import pytz

# 🧭 Carregar variáveis de ambiente
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
URL1 = os.getenv("URL1")
URL2 = os.getenv("URL2")

bot = Bot(token=TELEGRAM_TOKEN)

# 🕓 Função para obter horário local (Brasil)
def agora():
    tz = pytz.timezone("America/Sao_Paulo")
    return datetime.now(tz).strftime("%d/%m/%Y %H:%M:%S")

# 📩 Função para enviar mensagem ao Telegram
def enviar(msg):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

# 🌐 Função para obter conteúdo HTML
def obter_conteudo(url):
    try:
        resp = requests.get(url, timeout=20, verify=True)
        resp.raise_for_status()
        return resp.text, None
    except requests.exceptions.SSLError:
        # ⚠️ Caso o site tenha erro de certificado SSL, tenta novamente sem verificar
        try:
            resp = requests.get(url, timeout=20, verify=False)
            resp.raise_for_status()
            return resp.text, None
        except Exception as e:
            return None, f"SSL Error ignorado: {e}"
    except Exception as e:
        return None, str(e)

# 🔍 Função para gerar hash do conteúdo HTML
def gerar_hash(conteudo):
    return hashlib.sha256(conteudo.encode("utf-8")).hexdigest()

# 🧠 Função principal de verificação
def verificar_site(nome, url, hashes):
    conteudo, erro = obter_conteudo(url)

    if erro:
        enviar(f"⚠️ {nome} inacessível ({erro}), monitoramento ignorado hoje.")
        return hashes, None

    # Extrai texto puro para comparar alterações reais
    soup = BeautifulSoup(conteudo, "html.parser")
    texto = soup.get_text()
    hash_atual = gerar_hash(texto)

    if nome not in hashes:
        hashes[nome] = hash_atual
        return hashes, None

    if hash_atual != hashes[nome]:
        enviar(f"🚨 Mudança detectada em {nome}!\n{url}\n📅 {agora()}")
        hashes[nome] = hash_atual

    return hashes, None

# 🚀 Execução principal
def main():
    enviar(f"🚀 Iniciando monitoramento diário dos sites de concursos...\n\n"
           f"1️⃣ Câmara SJC: {URL1}\n2️⃣ Prefeitura Caçapava: {URL2}\n\n📅 {agora()}")

    hashes = {}

    # Verificar cada site
    hashes, _ = verificar_site("Câmara SJC", URL1, hashes)
    hashes, _ = verificar_site("Prefeitura Caçapava", URL2, hashes)

    enviar(f"✅ Monitoramento concluído!\n📅 {agora()}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        enviar(f"💥 Erro inesperado: {e}\n📅 {agora()}")
        print(f"Erro: {e}")
