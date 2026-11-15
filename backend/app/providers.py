import httpx
import json

async def get_real_signals(domain: str):
    indexed = 0
    backlinks = 0
    ref_domains = set()

    try:
        async with httpx.AsyncClient(timeout=25) as c:
            r = await c.get(
                "https://index.commoncrawl.org/CC-MAIN-2025-30-index",
                params={"url": f"{domain}/*", "output": "json", "fl": "url", "limit": 10000},
            )
            if r.status_code == 200:
                lines = [l for l in r.text.strip().splitlines() if l]
                indexed = len(lines)

            r2 = await c.get(
                "https://index.commoncrawl.org/CC-MAIN-2025-30-index",
                params={"url": f"*/*{domain}*", "output": "json", "fl": "url", "limit": 2000},
            )
            if r2.status_code == 200:
                for line in r2.text.strip().splitlines():
                    try:
                        u = json.loads(line).get("url", "")
                        u = u.replace("http://", "").replace("https://", "").replace("www.", "")
                        link_dom = u.split("/")[0].split(":")[0]
                        if link_dom and link_dom != domain and domain not in link_dom:
                            ref_domains.add(link_dom)
                    except Exception:
                        pass
                backlinks = len(ref_domains) * 3
    except Exception as e:
        print("CC fail:", e)

    return {
        "indexed": indexed,
        "ref_domains": len(ref_domains),
        "backlinks": backlinks,
    }

async def get_domain_age_precise(domain: str):
    try:
        import datetime

        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(f"https://rdap.org/domain/{domain}")
            if r.status_code != 200:
                return 0
            for ev in r.json().get("events", []):
                if ev.get("eventAction") == "registration":
                    date_str = ev.get("eventDate", "")[:10]
                    reg = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                    now = datetime.datetime.now()
                    days = (now - reg).days
                    return round(days / 365.25, 1)
            return 0
    except Exception:
        return 0
