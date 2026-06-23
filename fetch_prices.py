import json, urllib.request, sys
from datetime import datetime, timezone

def fetch_yahoo(symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read())
    return data['chart']['result'][0]['meta']['regularMarketPrice']

prices = {}

for symbol, key in [('VOO', 'VOO'), ('BBRI.JK', 'BBRI'), ('USDIDR=X', 'USDIDR')]:
    try:
        prices[key] = round(fetch_yahoo(symbol), 4)
        print(f"  {key}: {prices[key]}")
    except Exception as e:
        prices[key] = None
        print(f"  {key}: FAILED — {e}", file=sys.stderr)

prices['updated'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

with open('prices.json', 'w') as f:
    json.dump(prices, f, indent=2)

print(f"Done: {prices['updated']}")
