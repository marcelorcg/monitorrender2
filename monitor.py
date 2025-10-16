import os
import requests
from datetime import datetime
from telegram import Bot
from urllib3.exceptions import InsecureRequestWarning
import urllib3

# Ignora avisos SSL para sites confiáveis
urllib3.disable_warnings(InsecureRequestWarning)

# Pega os valores do GitHub Actions via environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=TELEGRAM_TOKEN)

# Sites a serem monitorados
sites = [
    {
        "nome": "Prefeitura de Caçapava",
        "url": "https://www.cacapava.sp.gov.br/publicacoes/concursos-publicos/concurso-publico-012024"
    },
    {
        "nome": "Câmara de São José dos Campos",
        "url": "https://www.camarasjc.sp.gov.br/a-camara/concurso-publico.php"
    }
]

def enviar_telegram(mensagem):
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=mensagem)

def verificar_site(site):
    try:
        response = requests.get(site["url"], headers={"User-Agent": "Mozilla/5.0"}, verify=False)
        status = response.status_code
        if status == 200:
            return f"✅ {site['nome']}: Site acessado com sucesso! (Status {status})"
        else:
            return f"🚨 {site['nome']}: Erro HTTP {status} ao acessar {site['url']}"
    except requests.exceptions.RequestException as e:
        return f"🚨 {site['nome']}: Erro ao acessar {site['url']}\n{e}"

def monitorar():
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    enviar_telegram(f"🚀 Monitoramento 24h iniciado pelo GitHub Actions!\n🕒 Verificação automática iniciada em {agora}")
    for site in sites:
        resultado = verificar_site(site)
        enviar_telegram(resultado)
    enviar_telegram("✅ Verificação concluída. Próxima em 2 horas ⏳")

if __name__ == "__main__":
    monitorar()
