import requests
import time
import os

# Pegando secrets do GitHub Actions
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Sites para monitorar
sites = [
    {"name": "Câmara SJC", "url": "https://www.camarasjc.sp.gov.br/a-camara/concurso-publico.php", "verify_ssl": False},
    {"name": "Prefeitura Caçapava", "url": "https://www.cacapava.sp.gov.br/publicacoes/concursos-publicos/concurso-publico-012024", "verify_ssl": True}
]

# Função para enviar Telegram
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        r = requests.post(url, data=payload)
        print(f"📩 Telegram status: {r.status_code}")
    except Exception as e:
        print(f"Erro ao enviar Telegram: {e}")

# Mensagem inicial
send_telegram("🚀 (Teste) Monitoramento 24h - execução iniciada no GitHub Actions.")

# Ciclos curtos de teste
for cycle in range(1, 4):  # 3 ciclos
    print(f"\n🔁 Test cycle {cycle}/3")
    for site in sites:
        print(f"⏳ Verificando {site['url']}...")
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        try:
            r = requests.get(site["url"], headers=headers, verify=site["verify_ssl"])
            print(f"✅ {site['name']} status: {r.status_code}")
        except requests.exceptions.SSLError as ssl_err:
            print(f"🚨 Erro SSL {site['name']}: {ssl_err}")
        except requests.exceptions.HTTPError as http_err:
            print(f"🚨 Erro HTTP {site['name']}: {http_err}")
        except Exception as e:
            print(f"🚨 Erro {site['name']}: {e}")
        send_telegram(f"Verificação {site['name']} feita com status ou erro acima.")

    print("⏳ Aguardando 10 segundos para próximo ciclo...")
    time.sleep(10)

send_telegram("✅ Teste de monitoramento curto finalizado.")
