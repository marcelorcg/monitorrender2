import os

telegram_token = os.getenv("TELEGRAM_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")

print("TELEGRAM_TOKEN =", telegram_token)
print("TELEGRAM_CHAT_ID =", chat_id)

if telegram_token and chat_id:
    print("✅ Variáveis estão definidas corretamente!")
else:
    print("❌ Variáveis NÃO estão definidas!")
