import yfinance as yf
from serpapi.google_search import GoogleSearch
from textblob import TextBlob
from fredapi import Fred
import pandas as pd
import requests
import os

# --- CONFIGURAÇÕES ---
SERPAPI_KEY = os.environ.get('SERPAPI_KEY')
FRED_API_KEY = os.environ.get('FRED_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

fred = Fred(api_key=FRED_API_KEY)

def send_telegram_alert(message):
    print(f"DEBUG: Tentando enviar: {message}")
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        params = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
        response = requests.get(url, params=params)
        print(f"DEBUG: Resposta Telegram: {response.status_code}")
    else:
        print("DEBUG: ERRO - Token/ChatID em falta!")

def check_market_danger(ticker, name):
    # Cálculo forçado para testar
    msg = f"TESTE DE FORÇA: {name} | Risco Detectado: 52.19"
    print(f"DEBUG: Enviando alerta forçado para {name}")
    send_telegram_alert(msg)

if __name__ == "__main__":
    check_market_danger("^GSPC", "S&P 500")
