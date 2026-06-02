import os
import requests

token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('TELEGRAM_CHAT_ID')

print("DEBUG: O SCRIPT monitor.py ESTÁ A CORRER!")

url = f"https://api.telegram.org/bot{token}/sendMessage"
params = {'chat_id': chat_id, 'text': "TESTE FINAL: O SCRIPT monitor.py FUNCIONA!"}

res = requests.get(url, params=params)
print(f"DEBUG: Resposta do Telegram: {res.status_code}")
