import requests
import hashlib
import os
from time import sleep
from dotenv import load_dotenv
from telegram import Bot

# Carrega variáveis do .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URLS = {
    "Caçapava": "https://www.cacapava.sp.gov.br/publicacoes/concursos-publicos/concurso-publico-012024",
    "São José": "https://www.camarasjc.sp.gov.br/a-camara/concurso-publico.php"
}

bot = Bot(token=TELEGRAM_TOKEN)

def get_hash(url):
    r = requests.get(url)
    r.raise_for_status()
    return hashlib.md5(r.text.encode("utf-8")).hexdigest()

def monitor():
    while True:
        for name, url in URLS.items():
            filename = f"{name}_hash.txt"
            old_hash = ""
            if os.path.exists(filename):
                with open(filename, "r") as f:
                    old_hash = f.read()

            try:
                new_hash = get_hash(url)
            except Exception as e:
                print(f"Erro ao acessar {url}: {e}")
                continue

            if new_hash != old_hash:
                with open(filename, "w") as f:
                    f.write(new_hash)
                message = f"🧩 Mudança detectada em {name}!"
                bot.send_message(chat_id=CHAT_ID, text=message)
                print(message)
            else:
                print(f"✅ Sem mudanças em {name}")
        sleep(60*60)  # verifica a cada 1 hora

if __name__ == "__main__":
    print("🚀 Monitoramento diário iniciado!")
    monitor()
