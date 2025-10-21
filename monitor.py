import os
import requests
import hashlib
import json
import datetime
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import telegram
import warnings

# 🔹 Ignorar warnings de certificado SSL não verificado
warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

# 🔹 Carregar variáveis do .env
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
URL1 = os.getenv("URL1")
URL2 = os.getenv("URL2")

# 🔹 Inicializa o bot do Telegram
bot = telegram.Bot(token=TELEGRAM_TOKEN)

# 🔹 Cabeçalhos para simular um navegador real
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/128.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9",
    "Referer": "https://www.google.com/",
}

# 🔹 Arquivo JSON para salvar os hashes
HASH_FILE = "hashes.json"

# 🔹 Função de envio seguro para o Telegram
def enviar_mensagem(msg):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)
        print("✅ Mensagem enviada no Telegram!")
    except Exception as e:
        print(f"⚠️ Erro ao enviar mensagem: {e}")

# 🔹 Função para pegar HTML e gerar hash
def obter_hash(url):
    for tentativa in range(5):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10, verify=False)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            conteudo = soup.get_text()
            return hashlib.sha256(conteudo.encode("utf-8")).hexdigest()
        except requests.exceptions.RequestException:
            continue
    return None

# 🔹 Carregar hashes salvos
if os.path.exists(HASH_FILE):
    with open(HASH_FILE, "r", encoding="utf-8") as f:
        hashes = json.load(f)
else:
    hashes = {}

# 🔹 Função para verificar alterações
def verificar_alteracao(nome, url):
    print(f"⏳ Verificando {nome} ({url})...")
    novo_hash = obter_hash(url)
    if novo_hash is None:
        print(f"⚠️ Não foi possível acessar {nome}, mas não enviaremos alerta 403.")
        return f"⚠️ {nome}: não foi possível acessar, mas monitoramento continua."

    antigo_hash = hashes.get(url)
    if antigo_hash != novo_hash:
        hashes[url] = novo_hash
        with open(HASH_FILE, "w", encoding="utf-8") as f:
            json.dump(hashes, f, ensure_ascii=False, indent=2)
        if antigo_hash is None:
            return f"⏳ {nome} verificado (primeiro monitoramento)."
        else:
            return f"🚨 Mudança detectada em {nome}!"
    else:
        return f"✅ {nome} não apresentou mudanças."

# 🔹 Execução principal
if __name__ == "__main__":
    agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    msg_inicio = (
        f"🚀 Monitoramento diário iniciado!\n\n"
        f"Sites verificados:\n"
        f"1️⃣ Câmara SJC: {URL1}\n"
        f"2️⃣ Prefeitura Caçapava: {URL2}"
    )
    enviar_mensagem(msg_inicio)

    status1 = verificar_alteracao("Câmara SJC", URL1)
    status2 = verificar_alteracao("Prefeitura Caçapava", URL2)

    enviar_mensagem(f"{status1}\n{status2}\n📅 {agora}\n✅ Monitoramento concluído!")
