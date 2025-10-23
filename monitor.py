import os
import json
import hashlib
import requests
from datetime import datetime
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
URL1 = os.getenv("URL1")
URL2 = os.getenv("URL2")

HASH_FILE = "hashes.json"

# Função para enviar mensagem no Telegram
def mensagem_telegram(texto):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": texto})
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

# Função para obter conteúdo da página
def obter_conteudo(url):
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.text

# Função para verificar site e detectar mudanças
def verificar_site(nome, url, hashes):
    try:
        conteudo = obter_conteudo(url)
        hash_novo = hashlib.sha256(conteudo.encode("utf-8")).hexdigest()
        if url in hashes and hashes[url] != hash_novo:
            mensagem_telegram(f"🚨 Mudança detectada em {nome}!\n{url}\n📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        hashes[url] = hash_novo
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403 and "cacapava" in url.lower():
            mensagem_telegram(f"⚠️ Prefeitura de Caçapava inacessível (403), monitoramento ignorado hoje.")
        else:
            mensagem_telegram(f"❌ Erro ao verificar {nome}: {e}")
    except Exception as e:
        mensagem_telegram(f"❌ Erro ao verificar {nome}: {e}")
    return hashes

# Carregar hashes existentes
if os.path.exists(HASH_FILE):
    with open(HASH_FILE, "r", encoding="utf-8") as f:
        hashes = json.load(f)
else:
    hashes = {}

# Mensagem inicial
mensagem_telegram(
    f"🚀 Iniciando monitoramento diário dos sites de concursos...\n\n"
    f"1️⃣ Câmara SJC: {URL1}\n"
    f"2️⃣ Prefeitura Caçapava: {URL2}\n\n"
    f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
)

# Verificar sites
hashes = verificar_site("Câmara SJC", URL1, hashes)
hashes = verificar_site("Prefeitura Caçapava", URL2, hashes)

# Salvar hashes atualizados
with open(HASH_FILE, "w", encoding="utf-8") as f:
    json.dump(hashes, f, indent=2, ensure_ascii=False)

mensagem_telegram(f"✅ Monitoramento concluído!\n📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
