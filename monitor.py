import os
import requests
import urllib3
from bs4 import BeautifulSoup
from telegram import Bot
import asyncio

# 🔇 Desativa o aviso de certificado SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 🔐 Variáveis de ambiente
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=TELEGRAM_TOKEN)

# 🌐 URLs dos sites
URLS = {
    "CACAPAVA": "https://www.cacapava.sp.gov.br/publicacoes/concursos-publicos/concurso-publico-012024",
    "CAMARA_SJC": "https://www.camarasjc.sp.gov.br/concursos-publicos"
}

# 📩 Função para enviar mensagens
async def enviar_mensagem(texto):
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=texto)

# 🔍 Função para verificar sites
async def verificar_sites():
    for nome, url in URLS.items():
        try:
            # Adiciona um User-Agent para evitar bloqueio 403
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, verify=False)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                texto = soup.get_text(strip=True)[:300]  # resumo dos 300 primeiros caracteres
                mensagem = f"✅ {nome}: Site acessado com sucesso!\n{url}\n\n{texto}\n✅ Verificação concluída. Próxima em 2 horas ⏳"
            else:
                mensagem = f"🚨 {nome}: Erro HTTP {response.status_code} ao acessar {url}"
        except Exception as e:
            mensagem = f"⚠️ {nome}: Erro ao acessar o site.\nDetalhes: {str(e)}"
        await enviar_mensagem(mensagem)

# 🚀 Executa o monitoramento
async def main():
    await enviar_mensagem("🚀 Monitoramento 24h iniciado pelo GitHub Actions!\n🕒 Verificação automática iniciada...")
    await verificar_sites()

if __name__ == "__main__":
    asyncio.run(main())
