import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import os
import pytz

# ==========================
# CONFIGURAÇÕES
# ==========================
URLS = [
    "https://www.cacapava.sp.gov.br/publicacoes",
    "https://www.camaracacapava.sp.gov.br/diario-oficial"
]
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TIMEZONE = pytz.timezone("America/Sao_Paulo")
ARQUIVO_ULTIMA_VERIFICACAO = "ultima_publicacao.txt"


# ==========================
# FUNÇÕES PRINCIPAIS
# ==========================

def enviar_telegram(mensagem):
    """Envia mensagem ao Telegram"""
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️ Variáveis TELEGRAM não configuradas.")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": mensagem}
    try:
        r = requests.post(url, data=data)
        if r.status_code == 200:
            print("📩 Mensagem enviada ao Telegram com sucesso!")
        else:
            print(f"❌ Erro ao enviar mensagem: {r.status_code}")
    except Exception as e:
        print(f"🚫 Falha ao enviar mensagem: {e}")


def obter_ultima_publicacao(url):
    """Obtém a última publicação da página"""
    try:
        resposta = requests.get(url, timeout=10)
        resposta.raise_for_status()
        soup = BeautifulSoup(resposta.text, "html.parser")
        item = soup.find("a")
        if item:
            return item.text.strip()
    except Exception as e:
        print(f"⚠️ Erro ao acessar {url}: {e}")
    return None


def carregar_ultima_publicacao():
    """Lê do arquivo a última publicação registrada"""
    if os.path.exists(ARQUIVO_ULTIMA_VERIFICACAO):
        with open(ARQUIVO_ULTIMA_VERIFICACAO, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None


def salvar_ultima_publicacao(titulo):
    """Salva no arquivo a última publicação detectada"""
    with open(ARQUIVO_ULTIMA_VERIFICACAO, "w", encoding="utf-8") as f:
        f.write(titulo)


def monitorar():
    """Monitora as URLs"""
    print("🔎 Verificando atualizações...")
    ultima_publicacao_salva = carregar_ultima_publicacao()
    nova_publicacao = None

    for url in URLS:
        titulo = obter_ultima_publicacao(url)
        if titulo and titulo != ultima_publicacao_salva:
            nova_publicacao = titulo
            salvar_ultima_publicacao(titulo)
            hora = datetime.now(TIMEZONE).strftime("%d/%m/%Y %H:%M")
            enviar_telegram(f"📢 Nova publicação encontrada em {url}\n🕓 {hora}\n📰 {titulo}")
            break

    if not nova_publicacao:
        print("⏳ Nenhuma nova publicação encontrada.")


# ==========================
# EXECUÇÃO PRINCIPAL
# ==========================
if __name__ == "__main__":
    print("🚀 Monitoramento diário iniciado!")

    # 🔹 Mensagem de teste (para verificar se o Telegram está funcionando)
    enviar_telegram("📡 Teste: o monitor está ativo no Railway! 🚀")

    monitorar()
    print("✅ Monitoramento concluído!")
