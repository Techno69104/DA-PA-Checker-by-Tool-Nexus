import math

def calculate_moz_like_da(indexed, ref_domains, age_years):
    if ref_domains == 0 and indexed == 0:
        return 1, 1, 1

    link_power = 0
    if ref_domains > 0:
        link_power = min(55, (math.log10(ref_domains + 1) * 18) - 5)

    idx_power = 0
    if indexed > 0:
        idx_power = min(15, math.log10(indexed + 1) * 5)

    age_power = min(15, age_years * 2.5)

    activity = 0
    if indexed > 5:
        activity = 5
    if indexed > 100:
        activity = 10
    if indexed > 1000:
        activity = 15

    da = int(round(link_power + idx_power + age_power + activity * 0.3))

    if ref_domains < 10:
        da = min(da, 8)
    elif ref_domains < 50:
        da = min(da, 20)
    elif ref_domains < 200:
        da = min(da, 35)

    da = max(1, min(99, da))
    pa = max(1, min(99, da - 2))

    if ref_domains < 20:
        spam = 2
    elif age_years < 1 and ref_domains > 1000:
        spam = 30
    else:
        spam = 5

    return da, pa, spam

def label(score):
    if score >= 81:
        return "Excellent"
    if score >= 61:
        return "Good"
    if score >= 41:
        return "Average"
    if score >= 21:
        return "Weak"
    return "Very Weak"
