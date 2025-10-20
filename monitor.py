import os
import requests
from bs4 import BeautifulSoup
import hashlib
import json
from datetime import datetime

# ⏳ Lê variáveis do Railway
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
URL1 = os.environ.get("URL1")
URL2 = os.environ.get("URL2")

# 🧩 Arquivo para armazenar os hashes
HASH_FILE = "hashes.json"

# 🔹 Função para enviar mensagem no Telegram
def send_telegram(message: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Variáveis TELEGRAM não configuradas.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        r = requests.post(url, data=data)
        if r.status_code == 200:
            print("✅ Mensagem enviada ao Telegram!")
        else:
            print(f"⚠️ Falha ao enviar mensagem: {r.status_code}")
    except Exception as e:
        print(f"⚠️ Erro ao enviar Telegram: {e}")

# 🔹 Função para obter hash do conteúdo da página
def get_hash(url):
    try:
        r = requests.get(url)
        r.raise_for_status()
        content = r.text
        return hashlib.md5(content.encode("utf-8")).hexdigest()
    except Exception as e:
        print(f"⚠️ Erro ao acessar {url}: {e}")
        return None

# 🔹 Carrega hashes existentes
if os.path.exists(HASH_FILE):
    with open(HASH_FILE, "r", encoding="utf-8") as f:
        hashes = json.load(f)
else:
    hashes = {}

# ⏳ Lista de URLs
urls = [URL1, URL2]

# 🔎 Verifica mudanças
for url in urls:
    print(f"⏳ Verificando {url}...")
    new_hash = get_hash(url)
    if new_hash is None:
        continue

    old_hash = hashes.get(url)
    if old_hash != new_hash:
        message = f"📢 Mudança detectada em {url}!\nHorário: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        send_telegram(message)
        hashes[url] = new_hash
    else:
        print(f"⏳ Nenhuma mudança em {url}.")
        # 🔹 Envia mensagem de teste mesmo sem mudança
        send_telegram(f"🧪 Teste de monitoramento para {url} — nenhuma mudança detectada.")

# 🔹 Salva hashes atualizados
with open(HASH_FILE, "w", encoding="utf-8") as f:
    json.dump(hashes, f, ensure_ascii=False, indent=2)

print("✅ Monitoramento concluído!")
