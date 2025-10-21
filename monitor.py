import os
import requests
import hashlib
import time
import telegram
import datetime
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# 🔹 Carregar variáveis do .env
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
URL1 = os.getenv("URL1")
URL2 = os.getenv("URL2")

# 🔹 Inicializa o bot do Telegram
bot = telegram.Bot(token=TELEGRAM_TOKEN)

# 🔹 Cabeçalhos para simular um navegador real (evita erro 403)
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/128.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9",
    "Referer": "https://www.google.com/",
}

# 🔹 Função de envio seguro para o Telegram
def enviar_mensagem(msg):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)
        print("✅ Mensagem enviada no Telegram!")
    except Exception as e:
        print(f"⚠️ Erro ao enviar mensagem: {e}")

# 🔹 Função para pegar HTML e gerar hash
def obter_hash(url):
    for tentativa in range(5):  # tenta até 5 vezes
        try:
            response = requests.get(url, headers=HEADERS, timeout=10, verify=False)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            conteudo = soup.get_text()
            return hashlib.sha256(conteudo.encode("utf-8")).hexdigest()
        except requests.exceptions.HTTPError as e:
            print(f"⚠️ Tentativa {tentativa + 1}/5 - HTTPError: {e}")
            time.sleep(2)
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Tentativa {tentativa + 1}/5 - Erro de rede: {e}")
            time.sleep(2)
    return None

# 🔹 Arquivos para salvar o hash antigo
HASH_CAMARA = "hash_camara.txt"
HASH_PREFEITURA = "hash_prefeitura.txt"

# 🔹 Função para comparar alterações
def verificar_alteracao(nome, url, arquivo_hash):
    print(f"⏳ Verificando {nome} ({url})...")
    novo_hash = obter_hash(url)
    if not novo_hash:
        enviar_mensagem(f"⚠️ HTTP Error ao acessar {url}\n{nome}")
        return f"{nome}: ❌ Erro ao acessar"

    if not os.path.exists(arquivo_hash):
        with open(arquivo_hash, "w") as f:
            f.write(novo_hash)
        print(f"🧩 Primeiro monitoramento de {nome} (hash salvo).")
        return f"{nome}: 🟢 Primeiro monitoramento, hash salvo."

    with open(arquivo_hash, "r") as f:
        antigo_hash = f.read()

    if novo_hash != antigo_hash:
        with open(arquivo_hash, "w") as f:
            f.write(novo_hash)
        enviar_mensagem(f"🚨 Mudança detectada em {nome}!\n{url}")
        return f"{nome}: 🔴 Mudança detectada!"
    else:
        return f"{nome}: ✅ Nenhuma mudança detectada."

# 🔹 Execução principal
if __name__ == "__main__":
    agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    msg_inicio = (
        f"🚀 Monitoramento diário iniciado!\n\nSites verificados:\n"
        f"1️⃣ Câmara SJC: {URL1}\n"
        f"2️⃣ Prefeitura Caçapava: {URL2}"
    )
    enviar_mensagem(msg_inicio)

    resultado_camara = verificar_alteracao("Câmara SJC", URL1, HASH_CAMARA)
    resultado_prefeitura = verificar_alteracao("Prefeitura Caçapava", URL2, HASH_PREFEITURA)

    msg_final = f"\n{resultado_camara}\n{resultado_prefeitura}\n📅 {agora}\n✅ Monitoramento concluído!"
    enviar_mensagem(msg_final)
