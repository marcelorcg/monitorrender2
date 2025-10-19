import requests
import time
import hashlib
from datetime import datetime
import os

# -------- CONFIGURAÇÃO TELEGRAM --------
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"Erro ao enviar Telegram: {e}")

# -------- FUNÇÃO DE MONITORAMENTO --------
def monitor(url, site_name, use_retries=False):
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"⏳ Verificando {url}...")

    # Path para salvar hash anterior
    hash_file = f"{site_name.replace(' ', '_')}_hash.txt"
    previous_hash = ""
    if os.path.exists(hash_file):
        with open(hash_file, "r") as f:
            previous_hash = f.read().strip()

    # Requisição com ou sem retry
    if use_retries:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
(KHTML, like Gecko) Chrome/118.0.5993.118 Safari/537.36",
            "Accept-Language": "pt-BR,pt;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        }
        max_attempts = 5
        for attempt in range(1, max_attempts + 1):
            try:
                response = requests.get(url, headers=headers, timeout=15)
                response.raise_for_status()
                content = response.text
                break
            except requests.exceptions.HTTPError as e:
                print(f"⚠️ Tentativa {attempt}/{max_attempts} - HTTPError: {e}")
                time.sleep(3)
        else:
            send_telegram(f"🚨 Erro ao acessar {url}: não foi possível acessar após {max_attempts} tentativas.\n📅 {timestamp}\n{url}")
            return
    else:
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            content = response.text
        except Exception as e:
            send_telegram(f"🚨 Erro ao acessar {url}: {e}\n📅 {timestamp}\n{url}")
            return

    # Calcular hash do conteúdo
    current_hash = hashlib.md5(content.encode("utf-8")).hexdigest()

    if previous_hash != current_hash:
        # Mudança detectada
        send_telegram(f"📅 {timestamp}\n🆕 Mudança detectada em {site_name}:\n{url}")
        with open(hash_file, "w") as f:
            f.write(current_hash)
        print(f"🧩 Mudança detectada em {site_name} (hash atualizado).")
    else:
        print(f"✅ Sem mudanças em {site_name}.")

# -------- URLs A MONITORAR --------
sites = [
    {"url": "https://www.camarasjc.sp.gov.br/a-camara/concurso-publico.php", "name": "Câmara SJC", "retries": False},
    {"url": "https://www.cacapava.sp.gov.br/publicacoes/concursos-publicos/concurso-publico-012024", "name": "Prefeitura Caçapava", "retries": True},
]

# -------- LOOP PRINCIPAL --------
print("🚀 Monitoramento diário iniciado!")
for site in sites:
    monitor(site["url"], site["name"], use_retries=site["retries"])
print("✅ Monitoramento concluído!")
