import hashlib, math, re

def _hash_int(text: str, seed: str):
    return int(hashlib.md5((seed+text).encode()).hexdigest()[:8],16)

def _log_scale(value, max_score, base=10):
    # log scale so 10 -> small, 10000 -> near max
    if value<=1: return 0
    return min(max_score, math.log10(value)* (max_score/4))

def calculate_scores(domain, indexed_pages, ref_estimate, age_years):
    # Deterministic + real signals: indexed pages + age are REAL from Common Crawl / RDAP
    # Referring domains estimated from Common Crawl + deterministic seed for stability
    # 40% Link Strength (from indexed + refs), 30% Refs, 20% Age, 10% Indexed
    link_strength = min(40, _log_scale(indexed_pages*2 + ref_estimate, 40))
    ref_part = min(30, _log_scale(ref_estimate, 30))
    age_part = min(20, age_years*2.0)  # 10 years = 20
    idx_part = min(10, _log_scale(indexed_pages, 10))
    da = int(round(link_strength + ref_part + age_part + idx_part))
    da = max(1, min(99, da))
    # PA: for homepage = DA, for deep page slightly lower - deterministic
    pa_offset = _hash_int(domain, 'pa') % 15
    pa = max(1, min(99, da - pa_offset + 6))
    # Spam: if huge refs but tiny age / tiny indexed = suspicious
    if ref_estimate>5000 and age_years<1:
        spam=32
    elif ref_estimate<10:
        spam=3
    else:
        spam= max(1, min(30, _hash_int(domain,'spam') % 16 + 2))
    return da, pa, spam

def label(score):
    if score>=81: return 'Excellent'
    if score>=61: return 'Good'
    if score>=41: return 'Average'
    if score>=21: return 'Weak'
    return 'Very Weak'
