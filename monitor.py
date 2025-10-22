import os
import hashlib
import requests
import json
import time
from datetime import datetime
from dotenv import load_dotenv
import subprocess

# Carrega variáveis de ambiente
load_dotenv()

# Configurações do Telegram
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# URLs dos sites
URLS = {
    "Câmara de SJC": os.getenv("URL1"),
    "Prefeitura de Caçapava": os.getenv("URL2"),
}

HASH_FILE = "hashes.json"

# 🔹 Função para enviar mensagem no Telegram
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Erro ao enviar mensagem ao Telegram: {e}")

# 🔹 Calcula hash do conteúdo
def get_hash(content):
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

# 🔹 Verifica os sites e detecta mudanças
def check_sites():
    print("🚀 Iniciando monitoramento diário dos sites...\n")
    send_telegram_message("🚀 Iniciando monitoramento diário dos sites de concursos...")

    # Carrega hashes antigos
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r") as f:
            hashes = json.load(f)
    else:
        hashes = {}

    for name, url in URLS.items():
        print(f"🌐 Verificando {name} → {url}")
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            new_hash = get_hash(response.text)

            old_hash = hashes.get(name)
            if old_hash and old_hash != new_hash:
                msg = f"⚠️ Mudança detectada em {name}!\n🔗 {url}"
                send_telegram_message(msg)
                print(msg)
            elif not old_hash:
                print(f"📄 Criado hash inicial para {name}.")
            else:
                print(f"✅ Nenhuma alteração detectada em {name}.")

            hashes[name] = new_hash

        except Exception as e:
            print(f"❌ Erro ao verificar {name}: {e}")
            send_telegram_message(f"❌ Erro ao verificar {name}: {e}")

    with open(HASH_FILE, "w") as f:
        json.dump(hashes, f, indent=4)

    print("\n💾 Hashes atualizados e salvos localmente.")

    # 🔁 Faz commit e push
    try:
        subprocess.run(["git", "add", "hashes.json"], check=True)
        subprocess.run(["git", "commit", "-m", "Atualização automática de hashes"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("✅ Commit e push concluídos com sucesso.")
    except Exception as e:
        print(f"⚠️ Falha ao fazer commit/push: {e}")

# 🔹 Aguardar até 9h da manhã
def wait_until_9am():
    now = datetime.now()
    target = now.replace(hour=9, minute=0, second=0, microsecond=0)
    if now > target:
        target = target.replace(day=now.day + 1)
    wait_seconds = (target - now).total_seconds()
    print(f"⏳ Aguardando até {target.strftime('%d/%m %H:%M')} para a próxima verificação diária...")
    time.sleep(wait_seconds)

if __name__ == "__main__":
    while True:
        check_sites()
        wait_until_9am()
