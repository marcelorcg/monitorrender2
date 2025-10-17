import os
import time
import requests
import urllib3
from telegram import Bot

# 🚫 Desativar avisos SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 🔒 Token e Chat ID vindos dos Secrets
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# 🤖 Inicializa o bot
bot = Bot(token=TELEGRAM_TOKEN)

# 🌐 URLs a serem monitoradas
URLS = {
    "Prefeitura de Caçapava": "https://www.cacapava.sp.gov.br/publicacoes/concursos-publicos",
    "Câmara de Caçapava": "https://www.camaracacapava.sp.gov.br/concursos",
}

# 💾 Cache inicializado (padrão)
CACHE_FILE = "cache.txt"
cache = {}

if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        for line in f:
            k, v = line.strip().split("=", 1)
            cache[k] = v
else:
    # Inicializa cache com valores padrão
    for nome, url in URLS.items():
        cache[nome] = ""
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        for nome, valor in cache.items():
            f.write(f"{nome}={valor}\n")

# 🕓 Intervalo entre verificações (em segundos)
INTERVALO = 300  # 5 minutos

print("🚀 Iniciando monitoramento 24h (Prefeitura e Câmara de Caçapava)...")

def salvar_cache():
    """Salva o conteúdo atual do cache no arquivo"""
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        for nome, valor in cache.items():
            f.write(f"{nome}={valor}\n")

def enviar_mensagem(mensagem):
    """Envia mensagem para o Telegram"""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=mensagem)
        print("📩 Mensagem enviada com sucesso ao Telegram.")
    except Exception as e:
        print(f"⚠️ Erro ao enviar mensagem: {e}")

def verificar_sites():
    """Verifica os sites em busca de alterações"""
    for nome, url in URLS.items():
        try:
            resposta = requests.get(url, verify=False, timeout=15)
            conteudo = resposta.text.strip()

            if cache.get(nome) != conteudo:
                if cache.get(nome):
                    mensagem = f"🔔 Atualização detectada em {nome}!\n{url}"
                    enviar_mensagem(mensagem)
                cache[nome] = conteudo
                salvar_cache()

            print(f"✅ Site {nome} verificado com sucesso.")
        except Exception as e:
            print(f"🚫 Erro ao acessar {nome}: {e}")

while True:
    verificar_sites()
    print(f"⏳ Aguardando {INTERVALO // 60} minutos para próxima verificação...\n")
    time.sleep(INTERVALO)
