import requests
import json
import os
from datetime import datetime
from telegram import Bot

# ==========================
# Configurações do Telegram
# ==========================
TELEGRAM_TOKEN = "SEU_TELEGRAM_TOKEN_AQUI"
TELEGRAM_CHAT_ID = "SEU_CHAT_ID_AQUI"
bot = Bot(token=TELEGRAM_TOKEN)

# ==========================
# URLs dos sites
# ==========================
sites = {
    "Prefeitura Caçapava": "https://www.cacapava.sp.gov.br/publicacoes/concursos-publicos/concurso-publico-012024",
    "Câmara SJC": "https://www.camarasjc.sp.gov.br/a-camara/concurso-publico.php"
}

# ==========================
# Pasta de cache
# ==========================
CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# ==========================
# Funções
# ==========================
def load_cache(site_name):
    path = os.path.join(CACHE_DIR, f"{site_name}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_cache(site_name, data):
    path = os.path.join(CACHE_DIR, f"{site_name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_site_content(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        response = requests.get(url, headers=headers, verify=False, timeout=15)
        response.raise_for_status()
        return response.text
    except requests.exceptions.HTTPError as e:
        return f"HTTP Error {e.response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"Request Error: {str(e)}"

def check_site(site_name, url):
    cache = load_cache(site_name)
    current_content = get_site_content(url)

    # Se conteúdo mudou ou não existe cache
    if cache.get("content") != current_content:
        # Atualiza cache
        save_cache(site_name, {"content": current_content, "last_checked": datetime.now().isoformat()})
        # Mensagem para Telegram
        message = f"🕒 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n📢 Site atualizado: {site_name}\n{url}"
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        return f"Alteração detectada e mensagem enviada para Telegram: {site_name}"
    else:
        return f"Sem alterações no site: {site_name}"

# ==========================
# Execução do monitoramento
# ==========================
if __name__ == "__main__":
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="🚀 Monitoramento 24h iniciado pelo GitHub Actions!")
    print("Monitoramento iniciado.")

    for site_name, url in sites.items():
        status = check_site(site_name, url)
        print(status)

    print("Verificação concluída. Próxima execução em 2 horas ⏳")
