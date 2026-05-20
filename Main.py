"""
Bus Stop Acceleration Priority Analysis
Debrecen Public Transport – Hackathon Tool  v2.0
 
Elemzések:
  1. Megálló-szintű prioritás (eredeti)
  2. Csomópont-szintű összesítés (azonos nevű megállók összevonva)
  3. Forgalmi kategória szerinti bontás (csúcs vs. alacsony forgalom)
  4. Hatékonysági kvadráns (várakozás vs. forgalom mátrix)
  5. Beavatkozási javaslatok típus szerint
"""
 
import pandas as pd
import numpy as np
 
# ── 1. Raw data ────────────────────────────────────────────────────────────────
raw = [
    (842,  "Kálvin tér",              6,    61,    160, 26.7,    17,  2.8,  177, 29.5,   64, 10.7,  207, 34.5, "3:31"),
    (427,  "Nagyerdei krt.",          6,  3439,     32,  5.3,   116, 19.3,  148, 24.7,  204, 34.0,  120, 20.0, "3:07"),
    (394,  "Medgyessy sétány",        6,  3439,     79, 13.2,     4,  0.7,   83, 13.8,  231, 38.5,  306, 51.0, "6:07"),
    (415,  "Nagyállomás",           530,  3456,   1280,  2.4,  5230,  9.9, 6510, 12.3, 7746, 14.6, 3796,  7.2, "1:57"),
    (125,  "Egyetem",                23,  3459,    267, 11.6,     5,  0.2,  272, 11.8,  231, 10.0,  493, 21.4, "3:01"),
    (115,  "Csokonai Színház",     1540,  8979,   7632,  5.0,  9602,  6.2,17234, 11.2,14349,  9.3,12368,  8.0, "2:05"),
    (853,  "Beszállítói Park",      131,   160,    723,  5.5,   691,  5.3, 1414, 10.8, 1431, 10.9, 1467, 11.2, "0:15"),
    (114,  "Csokonai Színház",     1562,  9038,   9858,  6.3,  6749,  4.3,16607, 10.6,10575,  6.8,13676,  8.8, "2:42"),
    (414,  "Nagyállomás",         1562,  6275,  14508,  9.3,   202,  0.1,14710,  9.4,  417,  3.7,14723,  9.4, "0:39"),
    (451,  "Pac",                  354,  1207,      0,  0.0,  3290,  9.3, 3290,  9.3, 3301,  9.3,    0,  0.0, "2:03"),
    (450,  "Pac",                  347,  1207,   3124,  9.0,     0,  0.0, 3124,  9.0,    0,  0.0, 3124,  9.0, "0:51"),
    (328,  "Klinikai Kp. Nagyerdei", 23,  3459,   164,  7.1,    40,  1.7,  204,  8.9,  107,  4.7,  231, 10.0, "2:04"),
    (412,  "Nagyállomás",         2528,  9649,      0,  0.0, 20466,  8.1,20466,  8.1,20471,  8.1,    0,  0.0, "2:04"),
    (855,  "Észak-Ny. Gazd. Öv.", 509,  1080,   1481,  2.9,  1984,  3.9, 3465,  6.8, 2781,  8.0, 2219,  9.7, "0:52"),
    (419,  "Nagyállomás",         1382,  6073,   4573,  3.3,  4573,  3.3, 9146,  6.6, 8628,  6.2, 8627, 16.3, "2:31"),
    (488,  "Rózsás Csárda",        395,  1489,    552,  1.4,  1920,  4.9, 2472,  6.3, 3737,  9.5, 2369,  6.0, "2:41"),
    (41,   "Balásházy János Szki.",104,   514,    118,  1.1,   532,  5.1,  650,  6.3,  714,  6.9,  300,  2.9, "1:05"),
    (680,  "Auchan Áruház",         48,   440,    126,  2.6,   174,  3.6,  300,  6.3,  174,  6.7,  126,  5.7, "1:03"),
    (551,  "Kálvin tér",          1140,  4641,   3278,  2.9,  3449,  3.0, 6727,  5.9,11406, 10.0,11227,  9.8, "1:24"),
    (413,  "Nagyállomás",         1728,  6337,   9537,  5.5,   474,  0.3,10011,  5.8,  851,  8.1, 9914,  5.7, "1:12"),
    (252,  "Kölcsey Kp.",         1008,  4498,   2767,  2.7,  2985,  3.0, 5752,  5.7, 9832,  9.8, 9598,  9.5, "1:41"),
    (65,   "Bem tér",                6,  3439,     13,  2.2,    21,  3.5,   34,  5.7,  218, 36.3,  210, 35.0, "2:59"),
    (417,  "Nagyállomás",          300,  1135,   1684,  5.6,     0,  0.0, 1684,  5.6,    0,  0.0, 1684,  5.6, "0:56"),
    (327,  "Klinikai Kp. Nagyerdei",749, 3105,   2371,  3.2,  1688,  2.3, 4059,  5.4, 6391,  8.5, 7056,  9.4, "2:06"),
    (35,   "Klinikai Kp. Auguszta", 372, 1425,   1552,  4.2,   376,  1.0, 1928,  5.2, 1799,  4.8, 3025,  8.1, "0:51"),
    (817,  "Krones Hungary",        200,  508,    435,  2.2,   590,  3.0, 1025,  5.1, 2084, 18.0, 1904,  9.5, "0:54"),
    (476,  "Rákóczi utca",         1014, 4559,   1362,  1.3,  3478,  3.4, 4840,  4.8,12014, 11.8, 9896,  9.8, "1:47"),
    (248,  "Honvéd utca",             6, 3439,      8,  1.3,    20,  3.3,   28,  4.7,  315, 52.5,  303, 50.5, "7:47"),
    (744,  "Károlyi M. u. villamos",  34,  92,    147,  4.3,     6,  0.2,  153,  4.5,  235,  6.9,  376, 11.1, "1:47"),
    (150,  "Dózsa György utca",     196, 1027,    655,  3.3,   224,  1.1,  879,  4.5, 1362,  6.9, 1794,  9.2, "1:36"),
    (563,  "Tiborc utca",           224, 1072,    967,  4.3,    34,  0.2, 1001,  4.5,  391,  1.7, 1324,  5.9, "1:13"),
    (490,  "Rózsás Csárda",         218,  800,    303,  1.4,   667,  3.1,  970,  4.4, 1462,  6.7, 1095,  5.0, "2:03"),
    (143,  "Dobozi lakótelep",      553, 2385,   1277,  2.3,  1155,  2.1, 2432,  4.4, 4825,  8.7, 4964,  9.0, "1:02"),
    (489,  "Rózsás Csárda",         594, 2856,   1978,  3.3,   614,  1.0, 2592,  4.4, 3425,  5.8, 4793,  8.1, "1:39"),
    (429,  "Nagymacs. Kastélykert", 131,  452,    163,  1.2,   408,  3.1,  571,  4.4,  643,  4.9,  393,  3.0, "1:04"),
]
 
columns = [
    "id", "name", "apc", "all",
    "in_sum", "in_avg", "out_sum", "out_avg",
    "freq_sum", "freq_avg",
    "occ_arr_sum", "occ_arr_avg",
    "occ_dep_sum", "occ_dep_avg",
    "delay_str"
]
 
df = pd.DataFrame(raw, columns=columns)
 
def parse_delay(s):
    parts = s.strip().split(":")
    return int(parts[0]) * 60 + int(parts[1])
 
def fmt_sec(s):
    return f"{int(s)//60}:{int(s)%60:02d}"
 
df["delay_sec"]       = df["delay_str"].apply(parse_delay)
df["total_flow"]      = df["in_sum"] + df["out_sum"]
df["avg_occupancy"]   = (df["occ_arr_avg"] + df["occ_dep_avg"]) / 2
df["passenger_delay"] = df["delay_sec"] * df["avg_occupancy"]
df["trips"]           = df["apc"]
 
def norm(series):
    mn, mx = series.min(), series.max()
    return (series - mn) / (mx - mn) if mx != mn else series * 0
 
df["n_delay"]           = norm(df["delay_sec"])
df["n_flow"]            = norm(df["total_flow"])
df["n_passenger_delay"] = norm(df["passenger_delay"])
df["n_occupancy"]       = norm(df["avg_occupancy"])
 
W_DELAY, W_FLOW, W_PDEL, W_OCC = 0.30, 0.25, 0.35, 0.10
 
df["priority_score"] = (
    W_DELAY * df["n_delay"] +
    W_FLOW  * df["n_flow"]  +
    W_PDEL  * df["n_passenger_delay"] +
    W_OCC   * df["n_occupancy"]
) * 100
 
df["priority_score"] = df["priority_score"].round(1)
df["rank"] = df["priority_score"].rank(ascending=False, method="min").astype(int)
 
SEP = "=" * 95
 
# ══════════════════════════════════════════════════════════════════════════════
# ELEMZÉS 1 – Megálló-szintű prioritáslista
# ══════════════════════════════════════════════════════════════════════════════
print(SEP)
print("  1. MEGÁLLÓ-SZINTŰ GYORSÍTÁSI PRIORITÁS")
print(SEP)
result = df[["rank","id","name","delay_str","total_flow","avg_occupancy",
             "passenger_delay","priority_score"]].sort_values("rank")
print(result.rename(columns={
    "rank":"Rang","id":"Kód","name":"Megálló","delay_str":"Várakozás",
    "total_flow":"Forgalom","avg_occupancy":"Átl.telít.",
    "passenger_delay":"Személy-mp","priority_score":"Pont"
}).to_string(index=False))
 
# ══════════════════════════════════════════════════════════════════════════════
# ELEMZÉS 2 – Csomópont-szintű összesítés
# ══════════════════════════════════════════════════════════════════════════════
print()
print(SEP)
print("  2. CSOMÓPONT-SZINTŰ ÖSSZESÍTÉS  (azonos nevű megállók összevonva)")
print(SEP)
 
node = df.groupby("name").agg(
    megallok          = ("id",              "count"),
    osszes_jarat      = ("apc",             "sum"),
    osszes_forgalom   = ("total_flow",      "sum"),
    atl_varakozas_sec = ("delay_sec",       "mean"),
    max_varakozas_sec = ("delay_sec",       "max"),
    osszes_szemelydel = ("passenger_delay", "sum"),
    atl_telitettseg   = ("avg_occupancy",   "mean"),
    osszes_pont       = ("priority_score",  "sum"),
).reset_index()
 
node["atl_varakozas"] = node["atl_varakozas_sec"].apply(fmt_sec)
node["max_varakozas"] = node["max_varakozas_sec"].apply(fmt_sec)
node["node_rank"]     = node["osszes_pont"].rank(ascending=False, method="min").astype(int)
node = node.sort_values("node_rank")
 
print(node[[
    "node_rank","name","megallok","osszes_jarat","osszes_forgalom",
    "atl_varakozas","max_varakozas","atl_telitettseg","osszes_szemelydel","osszes_pont"
]].rename(columns={
    "node_rank":        "Rang",
    "name":             "Csomópont neve",
    "megallok":         "Megállók",
    "osszes_jarat":     "Járatok",
    "osszes_forgalom":  "Össz.forgalom",
    "atl_varakozas":    "Átl.vár.",
    "max_varakozas":    "Max.vár.",
    "atl_telitettseg":  "Átl.telít.",
    "osszes_szemelydel":"Személyperc-veszt.",
    "osszes_pont":      "Össz.pont",
}).to_string(index=False))
 
print()
print("  ▶ TOP 3 beavatkozási csomópont:")
for _, row in node.head(3).iterrows():
    print(f"    #{int(row['node_rank'])}  {row['name']:<35}  "
          f"össz. forgalom: {int(row['osszes_forgalom']):>6}  "
          f"személyperc-veszteség: {row['osszes_szemelydel']:>10.0f}")
 
# ══════════════════════════════════════════════════════════════════════════════
# ELEMZÉS 3 – Forgalmi kategóriák (kvartilisek alapján)
# ══════════════════════════════════════════════════════════════════════════════
print()
print(SEP)
print("  3. FORGALMI KATEGÓRIÁK SZERINTI BONTÁS")
print(SEP)
 
q33 = df["total_flow"].quantile(0.33)
q66 = df["total_flow"].quantile(0.66)
 
def forgalmi_kat(f):
    if f <= q33:   return "🟢 Alacsony forgalom"
    elif f <= q66: return "🟡 Közepes forgalom"
    else:          return "🔴 Magas forgalom"
 
df["forgalmi_kat"] = df["total_flow"].apply(forgalmi_kat)
 
for kat in ["🔴 Magas forgalom", "🟡 Közepes forgalom", "🟢 Alacsony forgalom"]:
    sub = df[df["forgalmi_kat"] == kat].sort_values("priority_score", ascending=False)
    print(f"\n  {kat}  (forgalom küszöb: {q33:.0f} / {q66:.0f} utas)")
    print(f"  {'Megálló':<35} {'Várakozás':>10} {'Forgalom':>10} {'Pont':>8}")
    print(f"  {'-'*67}")
    for _, r in sub.iterrows():
        print(f"  {r['name']:<35} {r['delay_str']:>10} {int(r['total_flow']):>10} {r['priority_score']:>8.1f}")
 
# ══════════════════════════════════════════════════════════════════════════════
# ELEMZÉS 4 – Hatékonysági kvadráns
# ══════════════════════════════════════════════════════════════════════════════
print()
print(SEP)
print("  4. HATÉKONYSÁGI KVADRÁNS  (várakozás × forgalom mátrix)")
print(SEP)
 
med_delay = df["delay_sec"].median()
med_flow  = df["total_flow"].median()
 
def kvadrans(row):
    magas_var  = row["delay_sec"]   > med_delay
    magas_forg = row["total_flow"]  > med_flow
    if magas_var and magas_forg:
        return "A – KRITIKUS  (hosszú vár + nagy forgalom)"
    elif magas_var and not magas_forg:
        return "B – REJTETT   (hosszú vár, kis forgalom)"
    elif not magas_var and magas_forg:
        return "C – TERHELÉS  (rövid vár, nagy forgalom)"
    else:
        return "D – OPTIMÁLIS (rövid vár, kis forgalom)"
 
df["kvadrans"] = df.apply(kvadrans, axis=1)
 
print(f"  Medián várakozás: {fmt_sec(med_delay)}  |  Medián forgalom: {med_flow:.0f} utas\n")
for kv in sorted(df["kvadrans"].unique()):
    sub = df[df["kvadrans"] == kv].sort_values("priority_score", ascending=False)
    print(f"  ┌─ {kv} ({len(sub)} megálló)")
    for _, r in sub.iterrows():
        print(f"  │  [{r['id']:>3}] {r['name']:<33} vár: {r['delay_str']}  forgalom: {int(r['total_flow']):>6}  pont: {r['priority_score']:.1f}")
    print(f"  └─ Átl. pont: {sub['priority_score'].mean():.1f}  |  Össz. személyperc-veszt.: {sub['passenger_delay'].sum():,.0f}")
    print()
 
# ══════════════════════════════════════════════════════════════════════════════
# ELEMZÉS 5 – Beavatkozási javaslatok típus szerint
# ══════════════════════════════════════════════════════════════════════════════
print(SEP)
print("  5. BEAVATKOZÁSI JAVASLATOK TÍPUS SZERINT")
print(SEP)
 
def javaslat(row):
    delay  = row["delay_sec"]
    flow   = row["total_flow"]
    occ    = row["avg_occupancy"]
    if delay > 300:
        return "🚨 Azonnali beavatkozás – terminál/végállomás-kezelés felülvizsgálata"
    elif occ > 30 and delay > 120:
        return "🚌 Kapacitásbővítés + menetrendgyorsítás (zsúfolt + lassú)"
    elif flow > med_flow * 2 and delay > med_delay:
        return "⚡ Forgalomtechnikai beavatkozás – jelzőlámpa-prioritás javasolt"
    elif flow > med_flow * 2:
        return "📊 Menetrend-optimalizálás – csúcsidős sűrítés"
    elif delay > 120:
        return "⏱️  Megállókezelés gyorsítása – utas-áramlat design"
    else:
        return "✅git Elfogadható – megfigyelés elegendő"
 
df["javaslat"] = df.apply(javaslat, axis=1)
 
for jav_tip in df["javaslat"].unique():
    sub = df[df["javaslat"] == jav_tip].sort_values("priority_score", ascending=False)
    print(f"\n  {jav_tip}")
    for _, r in sub.iterrows():
        print(f"    [{r['id']:>3}] {r['name']:<35} pont: {r['priority_score']:.1f}")
 
print()
print(SEP)
print(f"  Súlyok: várakozás {W_DELAY*100:.0f}%  |  forgalom {W_FLOW*100:.0f}%  "
      f"|  személyperc {W_PDEL*100:.0f}%  |  telítettség {W_OCC*100:.0f}%")
print("  Hangolás: W_DELAY / W_FLOW / W_PDEL / W_OCC változók a script tetején.")
print(SEP)