import yfinance as yf
from serpapi.google_search import GoogleSearch
from textblob import TextBlob
from fredapi import Fred
import pandas as pd
import requests
import os

# --- CONFIGURAÇÕES ---
# As chaves são carregadas automaticamente pelo GitHub Actions a partir dos teus Secrets
SERPAPI_KEY = os.environ.get('SERPAPI_KEY')
FRED_API_KEY = os.environ.get('FRED_API_KEY')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

fred = Fred(api_key=FRED_API_KEY)

# MATRIZ INTEGRAL DE 200 TERMOS DE RISCO
RISK_TAXONOMY = {
    'CRITICAL': ['default', 'bankruptcy', 'liquidity crisis', 'margin call', 'bank run', 'solvency', 'collapse', 'insolvency', 'chapter 11', 'bond market crash', 'sovereign debt crisis', 'counterparty risk', 'fire sale', 'systemic risk', 'capital flight', 'bank failure', 'shadow banking', 'credit freeze', 'funding gap', 'bailout', 'haircut', 'contagion', 'bank holiday', 'distressed debt', 'repossession', 'bankrupt', 'financial collapse', 'credit default swap', 'subprime', 'negative equity', 'capital adequacy', 'run on bank', 'panic selling', 'fiat collapse', 'debt trap', 'credit crunch', 'seizure of assets', 'frozen accounts', 'hyperinflation', 'currency peg break'],
    'SEVERE': ['recession', 'inflation spike', 'stagflation', 'credit crunch', 'debt bubble', 'yield curve inversion', 'deflation', 'economic contraction', 'GDP decline', 'consumer confidence plummet', 'unemployment surge', 'structural unemployment', 'fiscal cliff', 'austerity', 'negative growth', 'productivity slump', 'commodity crash', 'depression', 'stagflationary', 'recessionary', 'trade war', 'supply chain collapse', 'commodity shortage', 'energy poverty', 'wage stagnation', 'cost of living crisis', 'poverty rate', 'business failure', 'layoffs', 'hiring freeze', 'corporate earnings miss', 'margin compression', 'market saturation', 'overcapacity', 'deindustrialization', 'protectionist policy', 'sovereign downgrade', 'fiscal mismanagement', 'public debt', 'unfunded liabilities'],
    'AI_SPECULATION': ['ai bubble', 'overvalued', 'hype', 'capex bubble', 'chip shortage', 'semiconductor cycle', 'ai valuation', 'tech bubble', 'compute overcapacity', 'data center cost', 'gpu glut', 'profitability gap', 'valuation bubble', 'meme stock', 'growth trap', 'nasdaq correction', 'tech selloff', 'automation bias', 'job displacement', 'r&d bubble', 'vc funding dry up', 'startup failure', 'unicorn bankruptcy', 'tech monopoly', 'antitrust probe', 'regulation risk', 'hallucination risk', 'ethical AI crisis', 'data privacy breach', 'cybersecurity threat', 'algorithmic bias', 'AI regulation', 'tech sector layoff', 'over-leveraged', 'speculative fervor', 'valuation disconnect', 'revenue shortfall', 'cash burn', 'burn rate', 'funding round failure'],
    'MACRO': ['fed hike', 'quantitative tightening', 'interest rates', 'fiscal deficit', 'debt ceiling', 'treasury yield spike', 'hawkish fed', 'monetary policy error', 'currency devaluation', 'fx volatility', 'trade deficit', 'geo-political risk', 'protectionism', 'tariffs', 'supply chain disruption', 'energy crisis', 'oil shock', 'labor shortage', 'central bank intervention', 'hawkish rhetoric', 'dovish pivot', 'global slowdown', 'emerging market crisis', 'capital controls', 'reserve currency war', 'geopolitical conflict', 'war risk', 'sanctions', 'energy dependence', 'dependency risk', 'commodity prices', 'inflationary pressure', 'disinflation', 'real wage decline', 'fiscal policy', 'tax hike', 'spending cut', 'sovereign risk', 'international trade', 'global recession'],
    'MARKET': ['volatility', 'flash crash', 'sell-off', 'panic', 'retail mania', 'short squeeze', 'gamma squeeze', 'algo trading error', 'market crash', 'bear market', 'investor pessimism', 'capital outflow', 'index rebalancing', 'dark pool', 'high frequency trading anomaly', 'liquidity dry up', 'derivatives exposure', 'market manipulation', 'insider trading', 'fraud detection', 'accounting scandal', 'sec probe', 'investigation', 'corporate governance failure', 'investor sentiment', 'market depth', 'bid-ask spread', 'slippage', 'liquidity trap', 'leverage ratio', 'debt-to-equity', 'margin debt', 'option volume', 'fear index', 'vix spike', 'market correction', 'downgrade', 'negative outlook', 'investor apathy', 'herd behavior']
}

def send_telegram_alert(message):
    print(f"DEBUG: A tentar enviar mensagem: {message}")
    print(f"DEBUG: Token: {'OK' if TELEGRAM_TOKEN else 'VAZIO'}")
    print(f"DEBUG: ChatID: {TELEGRAM_CHAT_ID}")
    
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        params = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
        try:
            response = requests.get(url, params=params)
            print(f"DEBUG: Resposta do Telegram: {response.status_code}")
            print(f"DEBUG: Corpo da resposta: {response.text}")
        except Exception as e:
            print(f"DEBUG: Erro de rede: {e}")
    else:
        print("DEBUG: ERRO CRÍTICO - Token ou ChatID não definidos no ambiente!")

def get_fed_liquidity():
    try:
        m2 = fred.get_series('M2SL')
        return float((m2.iloc[-1] - m2.iloc[-2]) / m2.iloc[-2])
    except: return 0.0

def get_weighted_sentiment():
    total_risk_score = 0
    weights = {'CRITICAL': 5.0, 'SEVERE': 3.0, 'AI_SPECULATION': 2.0, 'MACRO': 1.0, 'MARKET': 1.0}
    for cat, tags in RISK_TAXONOMY.items():
        for i in range(0, len(tags), 10):
            try:
                search = GoogleSearch({"engine": "google_news", "q": " OR ".join(tags[i:i+10]), "api_key": SERPAPI_KEY, "num": 3})
                for story in search.get_dict().get('news_results', []):
                    pol = TextBlob(story.get('title', '')).sentiment.polarity
                    if pol < 0: total_risk_score += (abs(pol) * weights[cat])
            except: continue
    return total_risk_score

def get_smart_money_metrics():
    y10, pcr = 4.5, 0.85
    try:
        tnx = yf.download("^TNX", period="1mo", progress=False)
        if not tnx.empty: y10 = float(tnx['Close'].iloc[-1])
        vix = yf.download("^VIX", period="1mo", progress=False)
        if not vix.empty: pcr = (float(vix['Close'].iloc[-1]) / 20.0)
    except: pass
    return y10, pcr

def check_market_danger(ticker, name):
    df = yf.download(ticker, period="5y", progress=False)
    close = df['Close'].iloc[:, 0] if isinstance(df['Close'], pd.DataFrame) else df['Close']
    z_score = (close - close.ewm(span=200).mean()) / close.rolling(200).std()
    liq = get_fed_liquidity()
    risk = get_weighted_sentiment()
    y10, pcr = get_smart_money_metrics()
    
    is_danger = (z_score.iloc[-1] > 2.0 or risk > 50.0) and (liq <= 0 or y10 > 4.5 or pcr > 1.1)
    
    status = "🚨 DANGER: ESTRUTURA FRÁGIL" if is_danger else "✅ NORMAL: Estável"
    msg = f"{status}\n{name} | Z-Score: {z_score.iloc[-1]:.2f} | Risco: {risk:.2f} | Yield: {y10:.2f}% | PCR: {pcr:.2f}"
    
    print(msg)
    if is_danger: 
        # MUDANÇA TEMPORÁRIA: Forçamos o envio para testar a ligação
    print("DEBUG: A forçar envio de teste...")
    send_telegram_alert(f"TESTE DE LIGAÇÃO: {name} | Risco calculado: {risk:.2f}")
    
    # O código original (que só envia se houver perigo) continua aqui em baixo
    if is_danger: 
        send_telegram_alert(msg)

if __name__ == "__main__":
    check_market_danger("^GSPC", "S&P 500")
    check_market_danger("^IXIC", "NASDAQ")
