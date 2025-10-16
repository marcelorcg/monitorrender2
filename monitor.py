import requests
import time
from datetime import datetime

# Configurações do Telegram via GitHub Secrets
TELEGRAM_TOKEN = "<seu_telegram_token>"
TELEGRAM_CHAT_ID = "<seu_chat_id>"

# Sites a monitorar
sites = [
    {
        "nome": "Câmara SJC",
        "url": "https://www.camarasjc.sp.gov.br/a-camara/concurso-publico.php"
    },
    {
        "nome": "Prefeitura Caçapava",
        "url": "https://www.cacapava.sp.gov.br/publicacoes/concursos-publicos/concurso-publico-012024"
    }
]

# Cabeçalhos para evitar bloqueio 403
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Função para enviar mensagem no Telegram
def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print(f"📩 Telegram status: {response.status_code}")
        else:
            print(f"⚠️ Falha Telegram: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao enviar Telegram: {e}")

# Mensagem inicial
send_telegram(f"🚀 Monitoramento 24h iniciado no GitHub Actions em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Loop principal de monitoramento contínuo
while True:
    for site in sites:
        print(f"⏳ Verificando {site['url']}...")
        try:
            response = requests.get(site['url'], headers=HEADERS, timeout=15, verify=True)
            if response.status_code == 200:
                msg = f"✅ {site['nome']} está online!"
            else:
                msg = f"⚠️ {site['nome']} retornou status {response.status_code}"
        except requests.exceptions.SSLError as ssl_err:
            msg = f"🚨 Erro SSL em {site['nome']}: {ssl_err}"
        except requests.exceptions.RequestException as e:
            msg = f"🚨 Erro ao acessar {site['nome']}: {e}"
        print(msg)
        send_telegram(msg)

    # Aguardar 1 hora antes do próximo ciclo (produção)
    time.sleep(3600)
