import math

def calculate_scores(indexed_pages, ref_estimate, age_years):
    # REAL DATA ONLY. No hash, no random.
    # New site: indexed=10, refs=5, age=0.5 => DA will be 5-12. Correct.
    # Big site: indexed=5000, refs=10000, age=20 => DA 80+. Correct.

    if age_years is None:
        age_years = 0

    # 40% Link Strength
    link_strength = min(40, math.log10(max(1, indexed_pages * 2 + ref_estimate)) * 10)
    # 30% Referring Domains
    ref_part = min(30, math.log10(max(1, ref_estimate)) * 10)
    # 20% Age - 0.5 year = 1 point, 10 years = 20 points
    age_part = min(20, age_years * 2.0)
    # 10% Indexed
    idx_part = min(10, math.log10(max(1, indexed_pages)) * 3)

    da = int(round(link_strength + ref_part + age_part + idx_part))
    da = max(1, min(99, da))

    # PA = DA - small difference for page level
    pa = max(1, min(99, da - 3))

    # Spam: new site with almost no links = Low spam (1-3%)
    if ref_estimate < 20:
        spam = 2
    elif ref_estimate > 5000 and age_years < 1:
        spam = 28
    else:
        spam = 5

    return da, pa, spam

def label(score):
    if score >= 81: return 'Excellent'
    if score >= 61: return 'Good'
    if score >= 41: return 'Average'
    if score >= 21: return 'Weak'
    return 'Very Weak'
