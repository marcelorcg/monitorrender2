# monitor.py
import os
import time
import json
import difflib
import requests
import urllib3
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

# Suprime warnings SSL para requests com verify=False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Carrega variáveis do .env (local) — no Railway use Service Variables
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# URLs: prioriza variáveis de ambiente (URL1/URL2). Se não existirem, usa defaults.
URL1 = os.getenv("URL1", "https://www.camarasjc.sp.gov.br/a-camara/concurso-publico.php")
URL2 = os.getenv("URL2", "https://www.cacapava.sp.gov.br/publicacoes/concursos-publicos/concurso-publico-012024")

if TELEGRAM_TOKEN is None or TELEGRAM_CHAT_ID is None:
    TELEGRAM_CONFIGURED = False
    print("⚠️ Variáveis TELEGRAM não configuradas (usar .env ou Service Variables).")
else:
    TELEGRAM_CONFIGURED = True

HASH_FILE = "hashes.json"

def enviar_telegram(mensagem):
    if not TELEGRAM_CONFIGURED:
        print("⚠️ TELEGRAM não configurado — mensagem não enviada:", mensagem)
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": mensagem}
    try:
        r = requests.post(url, data=data, timeout=15)
        r.raise_for_status()
        print("✅ Mensagem enviada no Telegram!")
    except Exception as e:
        print("⚠️ Erro ao enviar Telegram:", e)

def carregar_hashes():
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_hashes(hashes):
    with open(HASH_FILE, "w", encoding="utf-8") as f:
        json.dump(hashes, f, ensure_ascii=False, indent=2)

def fetch_with_retries(url, headers=None, verify=True, max_retries=5):
    """Faz GET com tentativas, expondo erros no log."""
    headers = headers or {}
    session = requests.Session()
    backoff = 1
    for attempt in range(1, max_retries + 1):
        try:
            resp = session.get(url, headers=headers, verify=verify, timeout=20)
            resp.raise_for_status()
            return resp.text
        except requests.exceptions.HTTPError as he:
            print(f"⚠️ Tentativa {attempt}/{max_retries} - HTTPError: {he}")
            if attempt == max_retries:
                raise
        except requests.exceptions.SSLError as se:
            print(f"⚠️ Tentativa {attempt}/{max_retries} - SSLError: {se}")
            if attempt == max_retries:
                raise
        except requests.exceptions.RequestException as re:
            print(f"⚠️ Tentativa {attempt}/{max_retries} - RequestException: {re}")
            if attempt == max_retries:
                raise
        time.sleep(backoff)
        backoff *= 2
    raise Exception("Erro: não foi possível buscar a URL após tentativas.")

def monitorar():
    tz = ZoneInfo("America/Sao_Paulo")
    hashes = carregar_hashes()

    sites = [
        # Câmara SJC: problema de certificado -> verify=False
        {
            "name": "Câmara SJC",
            "url": URL1,
            "verify": False,
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
        },
        # Prefeitura Caçapava: costuma responder 403 -> headers 'browser-like' + retries
        {
            "name": "Prefeitura Caçapava",
            "url": URL2,
            "verify": True,
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                "Referer": "https://www.cacapava.sp.gov.br/"
            }
        }
    ]

    for s in sites:
        name = s["name"]
        url = s["url"]
        verify = s.get("verify", True)
        headers = s.get("headers", {})
        print(f"⏳ Verificando {name} ({url})...")
        try:
            novo_conteudo = fetch_with_retries(url, headers=headers, verify=verify, max_retries=5)
            hash_antigo = hashes.get(url, "")
            if hash_antigo == "":
                print(f"🧩 Primeiro monitoramento de {name} (hash salvo).")
                hashes[url] = novo_conteudo
                salvar_hashes(hashes)
            elif hash_antigo != novo_conteudo:
                diff = list(difflib.unified_diff(
                    hash_antigo.splitlines(),
                    novo_conteudo.splitlines(),
                    lineterm=""
                ))
                texto_novo = "\n".join([linha[1:] for linha in diff if linha.startswith("+") and not linha.startswith("+++")])
                if not texto_novo.strip():
                    texto_novo = "(Mudança detectada, mas sem linhas claramente novas para exibir.)"
                msg = f"🆕 Atualização detectada em {name}!\n{url}\n\n{texto_novo}\n\n📅 {datetime.now(tz).strftime('%d/%m/%Y %H:%M:%S')}"
                print(msg)
                enviar_telegram(msg)
                hashes[url] = novo_conteudo
                salvar_hashes(hashes)
            else:
                print(f"✅ Sem mudanças em {name}.")
        except requests.exceptions.HTTPError as e:
            msg = f"⚠️ HTTP Error ao acessar {url}: {e}\n📅 {datetime.now(tz).strftime('%d/%m/%Y %H:%M:%S')}"
            print(msg)
            enviar_telegram(msg)
        except requests.exceptions.SSLError as e:
            msg = f"⚠️ Erro SSL ao acessar {url}: {e}\n📅 {datetime.now(tz).strftime('%d/%m/%Y %H:%M:%S')}"
            print(msg)
            enviar_telegram(msg)
        except Exception as e:
            msg = f"⚠️ Erro ao acessar {url}: {e}\n📅 {datetime.now(tz).strftime('%d/%m/%Y %H:%M:%S')}"
            print(msg)
            enviar_telegram(msg)

if __name__ == "__main__":
    print("🚀 Monitoramento diário iniciado!")
    monitorar()
    print("✅ Monitoramento concluído!")
