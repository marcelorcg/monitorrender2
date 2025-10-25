import os
import json
import requests
from hashlib import sha256
from time import sleep
from datetime import datetime
from dotenv import load_dotenv
from telegram import Bot
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Carrega variáveis do .env
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Inicializa bot Telegram
bot = Bot(token=BOT_TOKEN) if BOT_TOKEN and CHAT_ID else None

# Arquivos
SITES_FILE = "sites.txt"
HASH_FILE = "hashes.json"

# Configura retry com backoff
def requests_retry_session(
    retries=3,
    backoff_factor=1,
    status_forcelist=(500, 502, 503, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

# Função para calcular hash
def get_hash(content: str) -> str:
    return sha256(content.encode("utf-8")).hexdigest()

# Função para enviar Telegram
def enviar_telegram(mensagem: str):
    if bot:
        bot.send_message(chat_id=CHAT_ID, text=mensagem)
        print(f"✅ Telegram: {mensagem}")
    else:
        print("⚠️ Variáveis TELEGRAM não configuradas.")

# Carrega sites do arquivo sites.txt
def carregar_sites():
    sites = []
    if os.path.exists(SITES_FILE):
        with open(SITES_FILE, "r", encoding="utf-8") as f:
            for linha in f:
                url = linha.strip()
                if url:
                    sites.append(url)
    return sites

# Carrega hashes antigos
def carregar_hashes():
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Salva hashes atualizados
def salvar_hashes(hashes):
    with open(HASH_FILE, "w", encoding="utf-8") as f:
        json.dump(hashes, f, indent=4)

# Função principal de monitoramento
def monitorar():
    print(f"🚀 Monitoramento iniciado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    sites = carregar_sites()
    if not sites:
        print("⚠️ Nenhum site no sites.txt para monitorar.")
        return

    hashes_antigos = carregar_hashes()
    hashes_novos = hashes_antigos.copy()
    session = requests_retry_session()
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"}

    for url in sites:
        try:
            print(f"🌐 Acessando {url}")
            r = session.get(url, headers=headers, timeout=15, verify=False)
            r.raise_for_status()
            conteudo = r.text
            nova_hash = get_hash(conteudo)

            if url not in hashes_antigos or hashes_antigos[url] != nova_hash:
                enviar_telegram(f"🚨 Mudança detectada em {url}!")
                hashes_novos[url] = nova_hash
            else:
                print(f"✅ Nenhuma mudança: {url}")

        except requests.HTTPError as e:
            enviar_telegram(f"⚠️ Site inacessível: {url} ({e})")
        except requests.RequestException as e:
            enviar_telegram(f"⚠️ Erro ao acessar {url}: {e}")

    salvar_hashes(hashes_novos)
    print(f"✅ Monitoramento concluído em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

if __name__ == "__main__":
    monitorar()
