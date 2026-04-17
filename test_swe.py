import swisseph as swe
jd = swe.julday(2000, 1, 1, 12.0)
swe.set_sid_mode(swe.SIDM_LAHIRI)
cusps, ascmc = swe.houses_ex(jd, 28.6, 77.2, b'P', swe.FLG_SIDEREAL)
print(f"Len cusps: {len(cusps)}")
print(f"Index 0: {cusps[0]}")
print(f"Index 1: {cusps[1]}")
print(f"Index 12: {cusps[12]}")
