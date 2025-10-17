import os  # type: ignore
import requests  # type: ignore
import time  # type: ignore
import json  # type: ignore
from datetime import datetime  # type: ignore
from bs4 import BeautifulSoup  # type: ignore
from telegram import Bot  # type: ignore

# 🔐 Variáveis de ambiente (vindas do GitHub Secrets)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")  # type: ignore
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")  # type: ignore

bot = Bot(token=TELEGRAM_TOKEN)  # type: ignore

# 🕒 Caminho para o cache (salva último conteúdo conhecido)
CACHE_FILE = "cache_monitor.json"

# 🌐 Sites monitorados
SITES = {
    "CACAPAVA": "https://www.cacapava.sp.gov.br/publicacoes/concursos-publicos/concurso-publico-012024",
    "SJC": "https://www.camarasjc.sp.gov.br/a-camara/concurso-publico.php"
}


def carregar_cache():  # type: ignore
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {site: "" for site in SITES}


def salvar_cache(cache):  # type: ignore
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=4, ensure_ascii=False)


def obter_conteudo(url):  # type: ignore
    try:
        resposta = requests.get(url, verify=False, timeout=20)
        resposta.raise_for_status()
        soup = BeautifulSoup(resposta.text, "html.parser")
        return soup.get_text()
    except Exception as e:
        return f"ERRO: {e}"


def enviar_mensagem(mensagem):  # type: ignore
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=mensagem)


def main():  # type: ignore
    cache = carregar_cache()

    mensagem_inicial = (
        "🚀 Monitoramento 24h iniciado pelo GitHub Actions!\n"
        f"🕒 Verificação automática iniciada em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
    )
    enviar_mensagem(mensagem_inicial)

    for nome, url in SITES.items():
        conteudo_atual = obter_conteudo(url)
        conteudo_anterior = cache.get(nome, "")

        if "ERRO:" in conteudo_atual:
            enviar_mensagem(f"🚨 {nome}: {conteudo_atual}\n{url}")
        elif conteudo_atual != conteudo_anterior:
            enviar_mensagem(
                f"📢 {nome}: Detectada nova alteração no site!\n🔗 {url}\n"
                f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            )
            cache[nome] = conteudo_atual
        else:
            enviar_mensagem(f"✅ {nome}: Nenhuma alteração detectada.\n{url}")

    salvar_cache(cache)
    enviar_mensagem("✅ Verificação concluída. Próxima em 2 horas ⏳")


if __name__ == "__main__":  # type: ignore
    main()
