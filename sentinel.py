import os
import requests

token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('TELEGRAM_CHAT_ID')

print(f"DEBUG: A disparar teste de comunicação...")

url = f"https://api.telegram.org/bot{token}/sendMessage"
params = {'chat_id': chat_id, 'text': "TESTE DE LIGAÇÃO: O SCRIPT ESTÁ A FUNCIONAR!"}

res = requests.get(url, params=params)
print(f"DEBUG: Resposta do Telegram: {res.status_code}")
print(f"DEBUG: Conteúdo: {res.text}")
