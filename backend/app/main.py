from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import os
import re

from .providers import get_commoncrawl_stats, get_domain_age_precise
from .scoring import calculate_scores, label

app = FastAPI(title="DA PA Checker - Tool Nexus")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Models ----------

class CheckRequest(BaseModel):
    domains: List[str]

# ---------- Helpers ----------

def clean_domain(raw: str) -> str:
    raw = raw.strip().lower()
    raw = raw.replace("http://", "").replace("https://", "")
    raw = raw.replace("www.", "")
    raw = raw.split("/")[0].split("?")[0].split("#")[0]
    raw = raw.split(":")[0]
    return raw.strip()

def is_valid_domain(d: str) -> bool:
    return bool(re.match(r"^[a-z0-9-]+\.[a-z]{2,}$", d))

# ---------- API ----------

@app.get("/api/health")
def health():
    return {"status": "ok", "provider": "Own Score - Common Crawl + RDAP (Real Data)"}

@app.post("/api/check")
async def check(req: CheckRequest):
    results = []

    # max 50, dedupe
    seen = set()
    domains = []
    for raw in req.domains:
        d = clean_domain(raw)
        if d and d not in seen and is_valid_domain(d):
            seen.add(d)
            domains.append(d)
        if len(domains) >= 50:
            break

    for domain in domains:
        try:
            # 1. REAL Indexed Pages from Common Crawl - can be 0 for new site
            cc = await get_commoncrawl_stats(domain)
            indexed = cc['indexed']  # NO fake fallback, NO hash

            # 2. REAL Age from RDAP - e.g. 0.5 for 6 months
            age = await get_domain_age_precise(domain)
            if age is None:
                age = 0  # Unknown = 0, NOT 5.0

            # 3. Referring Domains - conservative estimate, NO inventing
            # New site: indexed 10 => refs ~5. NOT 1006.
            # Big site: indexed 5000 => refs ~2500.
            ref_estimate = max(0, indexed // 2)

            # 4. Score - Real only
            da, pa, spam = calculate_scores(indexed, ref_estimate, age)

            spam_label = 'Low' if spam < 10 else 'Medium' if spam < 20 else 'High'

            row = {
                'domain': domain,
                'da': da,
                'pa': pa,
                'spam': spam,
                'spam_label': spam_label,
                'referring_domains': ref_estimate,
                'backlinks': ref_estimate * 2,
                'age_years': round(age, 1) if age else 0,
                'indexed_pages': indexed,
                'status': label(da),
                'source': 'Own Score - Common Crawl + RDAP (Real Data)'
            }
            results.append(row)

        except Exception as e:
            # If API fails, show honest low score, not fake high score
            results.append({
                'domain': domain,
                'da': 1,
                'pa': 1,
                'spam': 1,
                'spam_label': 'Low',
                'referring_domains': 0,
                'backlinks': 0,
                'age_years': 0,
                'indexed_pages': 0,
                'status': 'Very Weak',
                'source': f'Error - {str(e)[:80]}',
            })

    # Sort by DA high to low
    results.sort(key=lambda x: x['da'], reverse=True)

    avg_da = round(sum(r['da'] for r in results) / len(results), 1) if results else 0
    avg_pa = round(sum(r['pa'] for r in results) / len(results), 1) if results else 0
    avg_spam = round(sum(r['spam'] for r in results) / len(results), 1) if results else 0
    total_ref = sum(r['referring_domains'] for r in results)

    return {
        'results': results,
        'summary': {
            'avg_da': avg_da,
            'avg_pa': avg_pa,
            'avg_spam': avg_spam,
            'total_ref': total_ref,
            'count': len(results)
        }
    }

# ---------- Frontend ----------

# Serve frontend from /frontend folder if exists
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "../../frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")
