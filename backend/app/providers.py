import httpx

async def get_commoncrawl_stats(domain: str):
    # FREE, NO KEY. Real count only. No fake fallback.
    try:
        async with httpx.AsyncClient(timeout=15) as c:
            r = await c.get(
                'https://index.commoncrawl.org/CC-MAIN-2025-30-index',
                params={'url': f'{domain}/*', 'output': 'json', 'fl': 'url', 'limit': 5000}
            )
            if r.status_code != 200:
                return {'indexed': 0, 'found': False}
            lines = [l for l in r.text.strip().splitlines() if l]
            return {'indexed': len(lines), 'found': True}
    except Exception:
        return {'indexed': 0, 'found': False}

async def get_domain_age(domain: str):
    # FREE RDAP. Real age only. Returns None if not found.
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(f'https://rdap.org/domain/{domain}')
            if r.status_code != 200:
                return None
            for ev in r.json().get('events', []):
                if ev.get('eventAction') == 'registration':
                    d = ev.get('eventDate', '')[:4]
                    if d.isdigit():
                        return max(0.1, 2026 - int(d) + (6/12 if False else 0))
            return None
    except Exception:
        return None

async def get_domain_age_precise(domain: str):
    # Returns years as float, e.g. 0.5 for 6 months
    try:
        import datetime
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(f'https://rdap.org/domain/{domain}')
            if r.status_code != 200:
                return None
            for ev in r.json().get('events', []):
                if ev.get('eventAction') == 'registration':
                    date_str = ev.get('eventDate', '')[:10]
                    reg = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                    now = datetime.datetime.now()
                    days = (now - reg).days
                    return round(days / 365.25, 1)
            return None
    except Exception:
        return None
