from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import os, re

from .providers import get_real_signals, get_domain_age_precise
from .scoring import calculate_moz_like_da, label

app = FastAPI(title="DA PA Checker - Tool Nexus")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class CheckRequest(BaseModel):
    domains: List[str]

def clean_domain(raw: str) -> str:
    raw = raw.strip().lower()
    raw = raw.replace("http://","").replace("https://","").replace("www.","")
    raw = raw.split("/")[0].split("?")[0].split("#")[0].split(":")[0]
    return raw.strip()

def is_valid_domain(d: str) -> bool:
    return bool(re.match(r"^[a-z0-9-]+\.[a-z]{2,}$", d))

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.post("/api/check")
async def check(req: CheckRequest):
    results = []
    seen = set()
    domains = []
    for raw in req.domains:
        d = clean_domain(raw)
        if d and d not in seen and is_valid_domain(d):
            seen.add(d); domains.append(d)
        if len(domains) >= 50: break

    for domain in domains:
        signals = await get_real_signals(domain)
        age = await get_domain_age_precise(domain)

        da, pa, spam = calculate_moz_like_da(
            signals['indexed'],
            signals['ref_domains'],
            age
        )

        results.append({
            'domain': domain,
            'da': da, 'pa': pa, 'spam': spam,
            'spam_label': 'Low' if spam < 10 else 'Medium' if spam < 20 else 'High',
            'referring_domains': signals['ref_domains'],
            'backlinks': signals['backlinks'],
            'age_years': round(age,1),
            'indexed_pages': signals['indexed'],
            'status': label(da),
            'source': 'Own Score - Calibrated to Moz Scale (Common Crawl + RDAP)'
        })

    results.sort(key=lambda x: x['da'], reverse=True)
    return {
        'results': results,
        'summary': {
            'avg_da': round(sum(r['da'] for r in results)/len(results),1) if results else 0,
            'avg_pa': round(sum(r['pa'] for r in results)/len(results),1) if results else 0,
            'avg_spam': round(sum(r['spam'] for r in results)/len(results),1) if results else 0,
            'total_ref': sum(r['referring_domains'] for r in results),
            'count': len(results)
        }
    }

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "../../frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")
