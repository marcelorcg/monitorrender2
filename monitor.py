import os
import requests
import hashlib
import time
from datetime import datetime
from requests.exceptions import RequestException

# 🔑 Variáveis de ambiente (Railway)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 🌎 Sites monitorados
SITES = [
    "https://www.camarasjc.sp.gov.br/a-camara/concurso-publico.php",
    "https://www.cacapava.sp.gov.br/publicacoes/concursos-publicos/concurso-publico-012024"
]

INTERVALO_MINUTOS = 60  # intervalo entre verificações

# 📤 Envio para Telegram
def enviar_telegram(mensagem):
    try:
        if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
            print("⚠️ Token ou Chat ID não configurados.")
            return
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": mensagem, "parse_mode": "HTML"}
        r = requests.post(url, data=data, timeout=10)
        r.raise_for_status()
        print(f"✅ Telegram: {mensagem[:70]}...")
    except Exception as e:
        print(f"⚠️ Erro ao enviar mensagem: {e}")

# 🔍 Baixa o conteúdo do site
def baixar_conteudo(url):
    try:
        print(f"🌐 Acessando {url}")
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
        r.raise_for_status()
        return r.text
    except Exception as e1:
        print(f"⚠️ Erro primário ({url}): {e1} — tentando ignorar SSL...")
        try:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=20, verify=False)
            r.raise_for_status()
            return r.text
        except Exception as e2:
            print(f"🚫 Falha total ({url}): {e2}")
            return None

# 🔐 Gera hash para detectar alterações
def gerar_hash(texto):
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()

# 🧠 Monitor principal (modo síncrono)
def monitorar():
    print(f"🚀 Monitoramento iniciado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    estados = {}

    while True:
        for site in SITES:
            conteudo = baixar_conteudo(site)

            if not conteudo:
                enviar_telegram(f"⚠️ Site inacessível: {site}")
                continue

            hash_novo = gerar_hash(conteudo)
            hash_antigo = estados.get(site)

            if hash_antigo and hash_novo != hash_antigo:
                msg = f"🚨 Mudança detectada em {site}!\n📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
                enviar_telegram(msg)
            else:
                print(f"✅ Nenhuma mudança: {site}")

            estados[site] = hash_novo

        print(f"✅ Ciclo concluído em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"⏳ Aguardando {INTERVALO_MINUTOS} minutos...\n")
        time.sleep(INTERVALO_MINUTOS * 60)

if __name__ == "__main__":
    print("🚀 Iniciando monitoramento diário 24h (modo síncrono confiável)...")
    monitorar()
