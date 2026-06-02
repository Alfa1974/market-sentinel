import os
import requests

token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('TELEGRAM_CHAT_ID')

print("DEBUG: O script main_sentinel.py está a correr!")

if token and chat_id:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {'chat_id': chat_id, 'text': "TESTE: O script está a funcionar!"}
    res = requests.get(url, params=params)
    print(f"DEBUG: Resposta Telegram: {res.status_code}")
else:
    print("DEBUG: ERRO: Credenciais em falta!")
