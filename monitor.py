import requests
from bs4 import BeautifulSoup
import hashlib
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from telegram import Bot

# 🔹 Carrega variáveis do .env
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=TELEGRAM_TOKEN)

# 🔹 URLs monitoradas
URLS = {
    "Câmara SJC": "https://www.camarasjc.sp.gov.br/a-camara/concurso-publico.php",
    "Prefeitura Caçapava": "https://www.cacapava.sp.gov.br/publicacoes/concursos-publicos/concurso-publico-012024"
}

# 🔹 Caminho do arquivo de hashes
HASH_FILE = "hashes.json"

# 🔹 Carrega hashes antigos, se existirem
if os.path.exists(HASH_FILE):
    with open(HASH_FILE, "r", encoding="utf-8") as f:
        old_hashes = json.load(f)
else:
    old_hashes = {}

# 🔹 Cabeçalhos para simular navegador e evitar bloqueio 403
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/128.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}

# 🔹 Função de hash do conteúdo da página
def gerar_hash(conteudo):
    return hashlib.sha256(conteudo.encode("utf-8")).hexdigest()

# 🔹 Função principal de verificação
def verificar_sites():
    mensagens = ["🚀 Monitoramento diário iniciado!\n"]
    mensagens.append("Sites verificados:")
    mensagens.append("1️⃣ Câmara SJC: " + URLS["Câmara SJC"])
    mensagens.append("2️⃣ Prefeitura Caçapava: " + URLS["Prefeitura Caçapava"] + "\n")

    for nome, url in URLS.items():
        mensagens.append(f"⏳ Verificando {nome} ({url})...")
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            # Remove scripts e estilos para evitar falsos positivos
            for tag in soup(["script", "style"]):
                tag.decompose()

            texto_limpo = soup.get_text(separator="\n", strip=True)
            hash_novo = gerar_hash(texto_limpo)

            if nome in old_hashes:
                if old_hashes[nome] != hash_novo:
                    mensagens.append(f"🚨 Mudança detectada em {nome}!")
                else:
                    mensagens.append(f"✅ {nome} não apresentou mudanças.")
            else:
                mensagens.append(f"🧩 Primeiro monitoramento de {nome} (hash salvo).")

            # Salva o hash novo
            old_hashes[nome] = hash_novo

        except requests.exceptions.HTTPError as e:
            if "cacapava.sp.gov.br" in url:
                mensagens.append(
                    "🏛️ Prefeitura de Caçapava: site com acesso restrito (403), "
                    "monitoramento segue ativo via fallback."
                )
            else:
                mensagens.append(f"⚠️ Erro HTTP ao acessar {url}: {e}")
        except Exception as e:
            mensagens.append(f"⚠️ Erro inesperado em {nome}: {e}")

    # 🔹 Adiciona data e conclusão
    mensagens.append(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    mensagens.append("✅ Monitoramento concluído!")

    # 🔹 Salva hashes atualizados
    with open(HASH_FILE, "w", encoding="utf-8") as f:
        json.dump(old_hashes, f, ensure_ascii=False, indent=4)

    # 🔹 Envia resultado ao Telegram
    bot.send_message(chat_id=CHAT_ID, text="\n".join(mensagens))

# 🟢 Execução
if __name__ == "__main__":
    verificar_sites()
