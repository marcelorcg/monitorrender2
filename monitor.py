# monitor.py

import os
import json
import difflib
from datetime import datetime
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright
import requests
from dotenv import load_dotenv

# 🔹 Carregar variáveis do .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 🔹 Verificar se as variáveis estão definidas
if TELEGRAM_TOKEN is None or TELEGRAM_CHAT_ID is None:
    raise ValueError("As variáveis TELEGRAM_TOKEN e TELEGRAM_CHAT_ID devem estar definidas!")

# 🔹 Arquivo para salvar hashes das páginas
HASH_FILE = "hashes.json"

# 🔹 Função de envio de mensagem pelo Telegram
def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": mensagem}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"⚠️ Erro ao enviar Telegram: {e}")

# 🔹 Carregar hashes salvos
def carregar_hashes():
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# 🔹 Salvar hashes atualizados
def salvar_hashes(hashes):
    with open(HASH_FILE, "w", encoding="utf-8") as f:
        json.dump(hashes, f, ensure_ascii=False, indent=2)

# 🔹 Função principal de monitoramento
def monitorar():
    tz = ZoneInfo("America/Sao_Paulo")  # horário de Brasília
    hashes = carregar_hashes()

    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_page(ignore_https_errors=True)

        sites = [
            "https://www.camarasjc.sp.gov.br/a-camara/concurso-publico.php",
            "https://www.cacapava.sp.gov.br/publicacoes/concursos-publicos/concurso-publico-012024"
        ]

        for site in sites:
            print(f"⏳ Verificando {site}...")
            try:
                page.goto(site, wait_until="load", timeout=30000)
                novo_conteudo = page.inner_text("body")  # texto visível da página

                hash_antigo = hashes.get(site, "")
                if hash_antigo == "":
                    print(f"🧩 Primeiro monitoramento de {site} (hash salvo).")
                    hashes[site] = novo_conteudo
                    salvar_hashes(hashes)
                elif hash_antigo != novo_conteudo:
                    # Detecta mudança e envia somente o texto novo
                    diff = list(difflib.unified_diff(
                        hash_antigo.splitlines(),
                        novo_conteudo.splitlines(),
                        lineterm=""
                    ))
                    texto_novo = "\n".join([linha[1:] for linha in diff if linha.startswith("+") and not linha.startswith("+++")])
                    msg = f"🆕 Atualização detectada em {site}!\n\n{texto_novo}\n\n📅 {datetime.now(tz).strftime('%d/%m/%Y %H:%M:%S')}"
                    print(msg)
                    enviar_telegram(msg)
                    hashes[site] = novo_conteudo
                    salvar_hashes(hashes)
                else:
                    print(f"✅ Sem mudanças em {site}.")
            except Exception as e:
                msg = f"🚨 Erro ao acessar {site}: {e}\n📅 {datetime.now(tz).strftime('%d/%m/%Y %H:%M:%S')}"
                print(msg)
                enviar_telegram(msg)

        browser.close()

# 🔹 Executar apenas uma vez
if __name__ == "__main__":
    print("🚀 Monitoramento diário iniciado!")
    monitorar()
    print("✅ Verificação concluída. Script finalizado.")
