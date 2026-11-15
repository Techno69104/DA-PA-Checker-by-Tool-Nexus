# DA PA Checker - YOUR OWN Unlimited Version (No Moz, No Keys, $0)

## What is this?
Your own Authority Score (0-100) calculated from FREE public data:
- Common Crawl (free, no key) - indexed pages
- RDAP / WHOIS (free, no key) - domain age
- Your own link-graph formula - DA / PA / Spam

No Moz API. No OpenPageRank key. No Brave. Unlimited checks.
Only limit YOU set: 5 checks per domain per day (to protect your server).

## Deploy on Render FIRST (Free)
1. Push this folder to GitHub
2. Render.com -> New -> Web Service -> Connect repo
3. Render auto-detects render.yaml
4. Deploy -> https://your-app.onrender.com
5. Test: google.com, youtube.com, yoursite.com

## Deploy on RackNerd LATER (Same code)
```bash
git clone YOUR_REPO_URL da-pa
cd da-pa
python3 -m venv venv && source venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
# Nginx -> port 8000
```

## API
POST /api/check  {domains: ["google.com"]}
GET /api/health
GET / -> frontend

## How Score Works (Transparent - show this on site)
DA = 40% Link Strength + 30% Referring Domains + 20% Domain Age + 10% Indexed Pages
PA = DA adjusted for specific page (same formula on page-level signals)
Spam = heuristic based on refs vs DA mismatch

## Limits (in backend/app/main.py)
- MAX_DOMAINS_PER_CHECK = 50
- MAX_CHECKS_PER_DOMAIN_PER_DAY = 5
- CACHE_DAYS = 30 (repeat checks are FREE, instant, no re-calculation)
- MAX_CHECKS_PER_IP_PER_DAY = 50
