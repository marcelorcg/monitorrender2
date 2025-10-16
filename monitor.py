import requests
from playwright.sync_api import sync_playwright
import time
import os

# Pegando os secrets do GitHub Actions
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Função para enviar mensagem ao Telegram
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg
    }
    response = requests.post(url, data=payload)
    print(f"📩 Telegram status: {response.status_code}")

# Sites a serem monitorados
SITES = [
    {"name": "Câmara de SJC", "url": "https://www.camarasjc.sp.gov.br/a-camara/concurso-publico.php", "method": "requests"},
    {"name": "Prefeitura de Caçapava", "url": "https://www.cacapava.sp.gov.br/publicacoes/concursos-publicos/concurso-publico-012024", "method": "playwright"}
]

# Mensagem inicial
send_telegram("✅ Mensagem inicial de teste enviada ao Telegram.")

# Ciclos curtos de teste
CYCLES = 3
DELAY = 10  # segundos

for cycle in range(1, CYCLES + 1):
    print(f"\n🔁 Test cycle {cycle}/{CYCLES}")
    for site in SITES:
        print(f"⏳ Verificando {site['url']}...")
        try:
            if site["method"] == "requests":
                # Ignora SSL para a Câmara de SJC
                r = requests.get(site["url"], verify=False, timeout=10)
                r.raise_for_status()
            elif site["method"] == "playwright":
                with sync_playwright() as p:
                    browser = p.firefox.launch()
                    page = browser.new_page()
                    page.goto(site["url"], timeout=15000)
                    browser.close()
            print(f"✅ {site['name']} acessado com sucesso!")
        except requests.exceptions.RequestException as e:
            print(f"🚨 Erro ao acessar {site['url']}: {e}")
        except Exception as e:
            print(f"🚨 Playwright erro ao acessar {site['url']}: {e}")
        send_telegram(f"⏳ Verificado {site['name']}: ciclo {cycle}/{CYCLES}")
    print(f"⏳ Aguardando {DELAY} segundos para próximo ciclo...")
    time.sleep(DELAY)

send_telegram("✅ Teste de monitoramento curto finalizado.")
