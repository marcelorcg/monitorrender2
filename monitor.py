import os
import json
import difflib
from datetime import datetime
from zoneinfo import ZoneInfo
import requests
from dotenv import load_dotenv
import urllib3

# 🔹 Suprime warnings de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 🔹 Carregar variáveis do .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if TELEGRAM_TOKEN is None or TELEGRAM_CHAT_ID is None:
    raise ValueError("As variáveis TELEGRAM_TOKEN e TELEGRAM_CHAT_ID devem estar definidas!")

HASH_FILE = "hashes.json"

def enviar_telegram(mensagem):
    """Envia mensagem pelo Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": mensagem}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"⚠️ Erro ao enviar Telegram: {e}")

def carregar_hashes():
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_hashes(hashes):
    with open(HASH_FILE, "w", encoding="utf-8") as f:
        json.dump(hashes, f, ensure_ascii=False, indent=2)

def monitorar():
    tz = ZoneInfo("America/Sao_Paulo")
    hashes = carregar_hashes()

    sites = [
        {
            "url": "https://www.camarasjc.sp.gov.br/a-camara/concurso-publico.php",
            "headers": {}  # SSL será ignorado, sem cabeçalho especial
        },
        {
            "url": "https://www.cacapava.sp.gov.br/publicacoes/concursos-publicos/concurso-publico-012024",
            "headers": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        }
    ]

    for site in sites:
        url = site["url"]
        headers = site.get("headers", {})
        print(f"⏳ Verificando {url}...")
        try:
            response = requests.get(url, headers=headers, verify=False, timeout=30)
            response.raise_for_status()
            novo_conteudo = response.text

            hash_antigo = hashes.get(url, "")
            if hash_antigo == "":
                print(f"🧩 Primeiro monitoramento de {url} (hash salvo).")
                hashes[url] = novo_conteudo
                salvar_hashes(hashes)
            elif hash_antigo != novo_conteudo:
                diff = list(difflib.unified_diff(
                    hash_antigo.splitlines(),
                    novo_conteudo.splitlines(),
                    lineterm=""
                ))
                texto_novo = "\n".join([linha[1:] for linha in diff if linha.startswith("+") and not linha.startswith("+++")])
                msg = f"🆕 Atualização detectada em {url}!\n\n{texto_novo}\n\n📅 {datetime.now(tz).strftime('%d/%m/%Y %H:%M:%S')}"
                print(msg)
                enviar_telegram(msg)
                hashes[url] = novo_conteudo
                salvar_hashes(hashes)
            else:
                print(f"✅ Sem mudanças em {url}.")
        except requests.exceptions.HTTPError as e:
            msg = f"🚨 Erro HTTP ao acessar {url}: {e}\n📅 {datetime.now(tz).strftime('%d/%m/%Y %H:%M:%S')}"
            print(msg)
            enviar_telegram(msg)
        except requests.exceptions.RequestException as e:
            msg = f"🚨 Erro ao acessar {url}: {e}\n📅 {datetime.now(tz).strftime('%d/%m/%Y %H:%M:%S')}"
            print(msg)
            enviar_telegram(msg)

if __name__ == "__main__":
    print("🚀 Monitoramento diário iniciado!")
    monitorar()
    print("✅ Monitoramento concluído!")
