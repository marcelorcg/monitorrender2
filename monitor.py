import requests
import hashlib
import os
from datetime import datetime
from telegram import Bot

# ---------------- CONFIGURAÇÃO ---------------- #
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

urls = {
    "Câmara SJC": "https://www.camarasjc.sp.gov.br/a-camara/concurso-publico.php",
    "Prefeitura Caçapava": "https://www.cacapava.sp.gov.br/publicacoes/concursos-publicos/concurso-publico-012024"
}

bot = Bot(token=TELEGRAM_TOKEN)
# ------------------------------------------------ #

def get_page_hash(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return hashlib.md5(r.text.encode('utf-8')).hexdigest()
    except Exception as e:
        print(f"Erro ao acessar {url}: {e}")
        return None

def load_last_hash(file_name):
    if os.path.exists(file_name):
        with open(file_name, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None

def save_hash(file_name, hash_value):
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(hash_value)

def send_telegram_message(text):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)
        print("Mensagem enviada com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar mensagem Telegram: {e}")

def main():
    print("🚀 Monitoramento diário iniciado!")
    for name, url in urls.items():
        current_hash = get_page_hash(url)
        if current_hash is None:
            continue
        file_name = f"{name.replace(' ', '_')}_hash.txt"
        last_hash = load_last_hash(file_name)
        if last_hash != current_hash:
            save_hash(file_name, current_hash)
            msg = f"🧩 Mudança detectada em {name} ({url})\n📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            send_telegram_message(msg)
        else:
            print(f"⏳ Nenhuma mudança em {name}")
    print("✅ Monitoramento concluído!\n")

if __name__ == "__main__":
    main()
