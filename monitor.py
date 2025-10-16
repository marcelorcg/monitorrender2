# monitor.py (modo de teste curto)
import os
import time
import json
import difflib
from datetime import datetime
from zoneinfo import ZoneInfo
import requests

# -------------------------------
# Configurações
# -------------------------------
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
HASH_FILE = "hashes.json"

# Sites que você já usa (mantidos)
SITES = [
    "https://www.camarasjc.sp.gov.br/a-camara/concurso-publico.php",
    "https://www.cacapava.sp.gov.br/publicacoes/concursos-publicos/concurso-publico-012024"
]

# Parâmetros do teste: pequenas esperas e poucas repetições
TEST_ITERATIONS = 3       # quantas vezes o loop de teste vai rodar
TEST_SLEEP_SECONDS = 10   # espera entre ciclos (10s para teste)

# -------------------------------
# Funções utilitárias
# -------------------------------
def carregar_hashes():
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_hashes(hashes):
    with open(HASH_FILE, "w", encoding="utf-8") as f:
        json.dump(hashes, f, ensure_ascii=False, indent=2)

def enviar_telegram(msg):
    if not (TELEGRAM_TOKEN and TELEGRAM_CHAT_ID):
        print("⚠️ Token ou Chat ID não definidos. Não foi possível enviar Telegram.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": msg}
    try:
        resp = requests.post(url, data=payload, timeout=10)
        print(f"📩 Telegram status: {resp.status_code}")
    except Exception as e:
        print(f"⚠️ Erro ao enviar mensagem no Telegram: {e}")

def diff_text(old, new):
    diff = list(difflib.unified_diff(old.splitlines(), new.splitlines(), lineterm=""))
    texto_novo = "\n".join([l[1:] for l in diff if l.startswith("+") and not l.startswith("+++")])
    return texto_novo.strip()

# -------------------------------
# Teste inicial para garantir envio (vai aparecer no Telegram quando o workflow rodar)
# -------------------------------
if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={"chat_id": TELEGRAM_CHAT_ID, "text": "🚀 (Teste) Monitoramento 24h - execução iniciada no GitHub Actions."},
            timeout=10
        )
        print("✅ Mensagem inicial de teste enviada ao Telegram.")
    except Exception as e:
        print(f"⚠️ Falha ao enviar mensagem inicial: {e}")
else:
    print("⚠️ Tokens do Telegram não encontrados nas variáveis de ambiente.")

# -------------------------------
# Lógica principal de monitoramento (modo de teste curto)
# -------------------------------
def monitor_once(hashes):
    tz = ZoneInfo("America/Sao_Paulo")
    for site in SITES:
        print(f"⏳ Verificando {site}...")
        try:
            resp = requests.get(site, timeout=30)
            resp.raise_for_status()
            conteudo = resp.text
            antigo = hashes.get(site, "")
            if antigo == "":
                hashes[site] = conteudo
                print(f"🧩 Primeiro monitoramento de {site} (hash salvo).")
            elif antigo != conteudo:
                texto_novo = diff_text(antigo, conteudo)
                horario = datetime.now(tz).strftime('%d/%m/%Y %H:%M:%S')
                msg = f"🆕 Atualização detectada em {site}!\n\n{(texto_novo[:1500] + '...') if len(texto_novo)>1500 else texto_novo}\n\n📅 {horario}"
                print(msg)
                enviar_telegram(msg)
                hashes[site] = conteudo
            else:
                print(f"✅ Sem mudanças em {site}.")
        except Exception as e:
            msg = f"🚨 Erro ao acessar {site}: {e}"
            print(msg)
            enviar_telegram(msg)
    return hashes

if __name__ == "__main__":
    hashes = carregar_hashes()
    # Loop de teste: roda TEST_ITERATIONS vezes com espera curta
    for i in range(TEST_ITERATIONS):
        print(f"\n🔁 Test cycle {i+1}/{TEST_ITERATIONS}")
        hashes = monitor_once(hashes)
        salvar_hashes(hashes)
        if i < TEST_ITERATIONS - 1:
            print(f"⏳ Aguardando {TEST_SLEEP_SECONDS} segundos para próximo ciclo...\n")
            time.sleep(TEST_SLEEP_SECONDS)
    print("✅ Teste de monitoramento curto finalizado.")
