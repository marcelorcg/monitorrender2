import os
import requests
import hashlib
import time
from datetime import datetime
from requests.exceptions import RequestException

# 🧠 Configurações
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

SITES = [
    "https://www.camarasjc.sp.gov.br/a-camara/concurso-publico.php",
    "https://www.cacapava.sp.gov.br/publicacoes/concursos-publicos/concurso-publico-012024"
]

INTERVALO_MINUTOS = 60  # ⏳ tempo entre verificações (60 = 1 hora)

# 🧰 Função para enviar mensagem ao Telegram
def enviar_telegram(mensagem):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Token ou Chat ID não configurados.")
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": mensagem, "parse_mode": "HTML"}
        requests.post(url, data=data, timeout=10)
        print(f"✅ Telegram: {mensagem[:80]}...")
    except Exception as e:
        print(f"⚠️ Erro ao enviar Telegram: {e}")

# 🔍 Função para verificar o conteúdo de cada site
def verificar_site(url):
    try:
        response = requests.get(
            url,
            timeout=20,
            verify=False,  # Ignora SSL inválido
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )

        # Trata o erro 403 como site acessível
        if response.status_code == 403:
            print(f"🔒 Acesso restrito, mas site online: {url}")
            return True, response.text

        response.raise_for_status()
        return True, response.text

    except RequestException as e:
        print(f"⚠️ Erro ao acessar {url}: {e}")
        return False, str(e)

# 💾 Gera um hash do conteúdo (para detectar mudanças)
def gerar_hash(conteudo):
    return hashlib.sha256(conteudo.encode("utf-8")).hexdigest()

# 🚨 Função principal do monitoramento
def monitorar_sites():
    print(f"🚀 Monitoramento iniciado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    estados_anteriores = {}

    while True:
        for site in SITES:
            ok, conteudo = verificar_site(site)

            if not ok:
                # Ignora falhas temporárias e não envia alerta
                continue

            hash_atual = gerar_hash(conteudo)
            hash_antigo = estados_anteriores.get(site)

            if hash_antigo and hash_atual != hash_antigo:
                mensagem = (
                    f"🚨 Mudança detectada em {site}!\n"
                    f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n{site}"
                )
                enviar_telegram(mensagem)
            else:
                print(f"✅ Sem mudanças: {site}")

            estados_anteriores[site] = hash_atual

        print(f"✅ Monitoramento concluído em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"⏳ Aguardando {INTERVALO_MINUTOS} minutos...\n")
        time.sleep(INTERVALO_MINUTOS * 60)

if __name__ == "__main__":
    print("🚀 Iniciando monitoramento diário 24h...")
    monitorar_sites()
