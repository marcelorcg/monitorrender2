import requests
import time
import os
import datetime
from telegram import Bot

# 🔐 Carregar variáveis de ambiente (definidas nos Secrets do GitHub)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 🚀 Inicializar o bot
bot = Bot(token=TELEGRAM_TOKEN)

# 🧭 Sites monitorados
SITES = {
    "Prefeitura de Caçapava": "https://www.cacapava.sp.gov.br/publicacoes/concursos-publicos/concurso-publico-012024",
    "Câmara de São José dos Campos": "https://www.camarasjc.sp.gov.br/a-camara/concurso-publico.php",
}

# 🧠 Configurações de headers (simula navegador)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0.0.0 Safari/537.36"
}

def enviar_mensagem(mensagem):
    """Envia mensagem ao Telegram."""
    try:
        bot.send_message(chat_id=CHAT_ID, text=mensagem)
    except Exception as e:
        print(f"Erro ao enviar mensagem ao Telegram: {e}")

def verificar_site(nome, url):
    """Verifica status do site e retorna resultado."""
    try:
        # Desabilita SSL verification apenas se necessário
        resposta = requests.get(url, headers=HEADERS, timeout=20, verify=False)
        resposta.raise_for_status()
        return f"✅ {nome}: Site acessado com sucesso! (Status {resposta.status_code})"
    except requests.exceptions.SSLError:
        return f"⚠️ {nome}: Erro SSL no certificado do site (tentando ignorar)."
    except requests.exceptions.HTTPError as e:
        return f"🚨 {nome}: Erro HTTP {e.response.status_code} ao acessar {url}"
    except requests.exceptions.RequestException as e:
        return f"🚫 {nome}: Erro de conexão ({e})"

def main():
    enviar_mensagem("🚀 Monitoramento 24h iniciado pelo GitHub Actions!")
    while True:
        hora_atual = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        enviar_mensagem(f"🕒 Verificação automática iniciada em {hora_atual}")
        
        for nome, url in SITES.items():
            resultado = verificar_site(nome, url)
            print(resultado)
            enviar_mensagem(resultado)
        
        enviar_mensagem("✅ Verificação concluída. Próxima em 2 horas ⏳")
        time.sleep(7200)  # ⏱️ 2 horas (7200 segundos)

if __name__ == "__main__":
    main()
