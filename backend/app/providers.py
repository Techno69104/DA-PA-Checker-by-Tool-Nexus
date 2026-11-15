import httpx, datetime

async def get_commoncrawl_stats(domain: str):
    # FREE, NO KEY. Counts indexed pages in latest Common Crawl.
    try:
        async with httpx.AsyncClient(timeout=12) as c:
            r=await c.get('https://index.commoncrawl.org/CC-MAIN-2025-30-index',
                params={'url': f'{domain}/*','output':'json','fl':'url','limit':2000})
            if r.status_code!=200:
                return {'indexed':0}
            lines=[l for l in r.text.strip().splitlines() if l]
            return {'indexed': len(lines)}
    except Exception:
        return {'indexed':0}

async def get_domain_age(domain: str):
    # FREE, NO KEY via RDAP
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r=await c.get(f'https://rdap.org/domain/{domain}')
            if r.status_code!=200: return 5.0
            for ev in r.json().get('events',[]):
                if ev.get('eventAction')=='registration':
                    d=ev.get('eventDate','')[:4]
                    if d.isdigit():
                        return max(0.5, 2026-int(d))
            return 5.0
    except Exception:
        return 5.0
