import requests
import time
from datetime import datetime
from telegram import Bot
import urllib3

# -----------------------------
# Configurações
# -----------------------------
TELEGRAM_TOKEN = "SEU_TELEGRAM_TOKEN_AQUI"
TELEGRAM_CHAT_ID = "SEU_CHAT_ID_AQUI"

URLS = {
    "Câmara SJC": "https://www.camarasjc.sp.gov.br/a-camara/concurso-publico.php",
    "Prefeitura Caçapava": "https://www.cacapava.sp.gov.br/publicacoes/concursos-publicos/concurso-publico-012024"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/116.0.0.0 Safari/537.36"
}

INTERVALO_HORAS = 2  # intervalo entre verificações

# -----------------------------
# Inicializar bot Telegram
# -----------------------------
bot = Bot(token=TELEGRAM_TOKEN)

def enviar_telegram(mensagem):
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=mensagem)

# -----------------------------
# Suprimir warnings SSL
# -----------------------------
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# -----------------------------
# Loop principal
# -----------------------------
enviar_telegram("🚀 Monitoramento 24h iniciado pelo GitHub Actions!")

while True:
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    enviar_telegram(f"🕒 Verificação automática iniciada em {timestamp}")

    for nome, url in URLS.items():
        try:
            if "cacapava" in url:
                # Ignorar SSL
                response = requests.get(url, headers=HEADERS, verify=False, timeout=30)
            else:
                response = requests.get(url, headers=HEADERS, timeout=30)

            if response.status_code == 200:
                enviar_telegram(f"✅ {nome}: Site acessado com sucesso! (Status 200)")
            else:
                enviar_telegram(f"⚠️ {nome}: Status HTTP {response.status_code}")

        except requests.exceptions.RequestException as e:
            enviar_telegram(f"🚨 {nome}: Erro ao acessar {url}\n{str(e)}")

    enviar_telegram(f"✅ Verificação concluída. Próxima em {INTERVALO_HORAS} horas ⏳")
    time.sleep(INTERVALO_HORAS * 3600)
