import os
import requests
from bs4 import BeautifulSoup
import json
import datetime
import time
from telegram import Bot
import urllib3

# Ignorar avisos SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Telegram
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
bot = Bot(token=TELEGRAM_TOKEN)

# URLs a monitorar
SITES = {
    "CACAPAVA": "https://www.cacapava.sp.gov.br/publicacoes/concursos-publicos/concurso-publico-012024",
    "SJC": "https://www.camarasjc.sp.gov.br/a-camara/concurso-publico.php"
}

# Cache para comparar alterações
CACHE_FILE = "cache.json"

# Inicializa cache vazio se não existir
if not os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "w") as f:
        json.dump({}, f)

# Função para enviar mensagens Telegram
def enviar_mensagem(texto):
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=texto)

# Função para buscar conteúdo da página
def buscar_site(nome, url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            return response.text
        else:
            return f"ERRO HTTP {response.status_code}"
    except Exception as e:
        return f"ERRO: {e}"

# Função principal
def main():
    while True:
        agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        enviar_mensagem(f"🚀 Monitoramento 24h iniciado pelo GitHub Actions!\n🕒 Verificação automática iniciada em {agora}")
        
        # Carrega cache
        with open(CACHE_FILE, "r") as f:
            cache = json.load(f)
        
        for nome, url in SITES.items():
            conteudo_atual = buscar_site(nome, url)
            
            if nome in cache:
                if conteudo_atual != cache[nome]:
                    enviar_mensagem(f"⚡ {nome}: Conteúdo atualizado no site!\n{url}")
                else:
                    print(f"{nome}: sem alterações detectadas.")
            else:
                # primeira execução
                enviar_mensagem(f"✅ {nome}: monitoramento iniciado.\n{url}")
            
            # Atualiza cache
            cache[nome] = conteudo_atual
        
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f)
        
        enviar_mensagem("✅ Verificação concluída. Próxima em 2 horas ⏳")
        time.sleep(7200)  # 2 horas

if __name__ == "__main__":
    main()
