import os
import time
import requests
import hashlib
import asyncio
from telegram import Bot

# 🔒 Variáveis de ambiente do GitHub Secrets
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# 🤖 Inicializa o bot
bot = Bot(token=TELEGRAM_TOKEN)

# 🧩 Cache de conteúdo (evita avisos repetidos)
cache = {
    "cacapava": "",
    "sjc": ""
}

# 📨 Envio de mensagens com asyncio.run()
def enviar_mensagem(texto):
    try:
        asyncio.run(bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=texto))
        print("✅ Mensagem enviada com sucesso ao Telegram.")
    except Exception as e:
        print(f"⚠️ Erro ao enviar mensagem: {e}")

# 🌐 Função para verificar se houve mudança no site
def verificar_site(nome, url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        # SSL ignorado (confia no site)
        response = requests.get(url, headers=headers, verify=False, timeout=15)
        response.raise_for_status()

        # Gera hash do conteúdo HTML
        novo_hash = hashlib.sha256(response.text.encode("utf-8")).hexdigest()

        # Se cache estiver vazio, apenas inicializa
        if cache[nome] == "":
            cache[nome] = novo_hash
            print(f"🔹 Cache inicializado para {nome}")
            return

        # Se houve alteração no hash → site mudou
        if cache[nome] != novo_hash:
            cache[nome] = novo_hash
            mensagem = f"🔔 Mudança detectada no site {nome.upper()}!\n{url}"
            enviar_mensagem(mensagem)
            print(mensagem)
        else:
            print(f"✅ Nenhuma mudança detectada em {nome}")

    except requests.exceptions.HTTPError as e:
        enviar_mensagem(f"🚨 {nome.upper()}: Erro HTTP {e.response.status_code} ao acessar {url}")
    except Exception as e:
        enviar_mensagem(f"⚠️ {nome.upper()}: Erro inesperado: {e}")

# 🚀 Envio de início
enviar_mensagem("🚀 Monitoramento 24h iniciado pelo GitHub Actions!")

# 🔁 Loop contínuo — verifica a cada 2 horas
while True:
    enviar_mensagem("🕒 Verificação automática iniciada...")
    verificar_site("cacapava", "https://www.cacapava.sp.gov.br/publicacoes/concursos-publicos/concurso-publico-012024")
    verificar_site("sjc", "https://www.camarasjc.sp.gov.br/a-camara/concurso-publico.php")
    enviar_mensagem("✅ Verificação concluída. Próxima em 2 horas ⏳")
    time.sleep(7200)  # 2 horas (7200 segundos)
