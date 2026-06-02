import requests
import os

TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

print(f"DEBUG: Token detetado? {'SIM' if TOKEN else 'NAO'}")
print(f"DEBUG: ChatID detetado? {CHAT_ID}")

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
params = {'chat_id': CHAT_ID, 'text': "TESTE DE LIGAÇÃO EFETUADO COM SUCESSO!"}

response = requests.get(url, params=params)
print(f"DEBUG: Resposta do Telegram: {response.status_code}")
print(f"DEBUG: Corpo da resposta: {response.text}")
