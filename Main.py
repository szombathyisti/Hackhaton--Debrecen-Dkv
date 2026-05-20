"""
Bus Stop Acceleration Priority Analysis
Debrecen Public Transport – Hackathon Tool  v3.0
 
Adatforrás: 04.csv  (Summary stop stats export)
CSV fejléc: 6 sor metaadat, utána adatsorok vesszővel elválasztva.
 
Delay formátum a CSV-ben: nap-arány (pl. 0.00215... = ~3:06 perc)
→ átváltás: * 24 * 60 = percek, * 24 * 3600 = másodpercek
 
Elemzések:
  1. Megálló-szintű prioritás
  2. Csomópont-szintű összesítés
  3. Forgalmi kategóriák szerinti bontás
  4. Hatékonysági kvadráns
  5. Beavatkozási javaslatok típus szerint
"""
 
import pandas as pd
import numpy as np
import sys
import os
 
# ── 1. CSV betöltés ────────────────────────────────────────────────────────────
CSV_PATH = "04.csv"
 
if not os.path.exists(CSV_PATH):
    print(f"HIBA: Nem található a(z) '{CSV_PATH}' fájl!")
    print(f"  Elvárt helye: {os.path.abspath(CSV_PATH)}")
    sys.exit(1)
 
# Az első 6 sor metaadat (Summary stop stats, Selected days, stb.) – kihagyjuk
# A 7. sor a dupla fejléc (Stop/Stop/Planned stopping...) – kihagyjuk
# A 8. sor a típusjelzők (Ident./Name/APC...) – ez lesz a header
df_raw = pd.read_csv(
    CSV_PATH,
    skiprows=6,       # 6 sor metaadat átugrása
    header=0,         # következő sor = oszlopnevek
    dtype=str,        # mindent stringként olvasunk be először
)
 
# Oszlopok átnevezése (a CSV dupla fejléce miatt előfordulhat .1 suffix)
# Elvárt oszloprend: Ident., Name, APC, All, Σ(in), Ø(in), Σ(out), Ø(out),
#                   Σ(freq), Ø(freq), Σ(occ_arr), Ø(occ_arr), Σ(occ_dep), Ø(occ_dep), Ø(delay)
col_names = [
    "id", "name", "apc", "all",
    "in_sum", "in_avg",
    "out_sum", "out_avg",
    "freq_sum", "freq_avg",
    "occ_arr_sum", "occ_arr_avg",
    "occ_dep_sum", "occ_dep_avg",
    "delay_day"     # nap-arány formátum
]
 
# Csak az első 15 oszlopot vesszük (esetleges extra oszlopok eldobva)
df_raw = df_raw.iloc[:, :15]
df_raw.columns = col_names
 
# Üres sorok eltávolítása
df_raw = df_raw.dropna(subset=["id", "name"]).reset_index(drop=True)
 
# Numerikus konverzió
num_cols = ["apc", "all", "in_sum", "in_avg", "out_sum", "out_avg",
            "freq_sum", "freq_avg", "occ_arr_sum", "occ_arr_avg",
            "occ_dep_sum", "occ_dep_avg", "delay_day"]
 
for col in num_cols:
    df_raw[col] = pd.to_numeric(df_raw[col], errors="coerce").fillna(0.0)
 
df = df_raw.copy()
 
# ── 2. Delay konverzió: nap-arány → másodperc + mm:ss string ──────────────────
def day_to_sec(d):
    return d * 24 * 3600
 
def fmt_sec(s):
    s = int(round(s))
    return f"{s // 60}:{s % 60:02d}"
 
df["delay_sec"] = df["delay_day"].apply(day_to_sec)
df["delay_str"] = df["delay_sec"].apply(fmt_sec)
 
# ── 3. Levezetett mutatók ──────────────────────────────────────────────────────
df["total_flow"]      = df["in_sum"] + df["out_sum"]
df["avg_occupancy"]   = (df["occ_arr_avg"] + df["occ_dep_avg"]) / 2
df["passenger_delay"] = df["delay_sec"] * df["avg_occupancy"]
 
# ── 4. Normalizálás 0–1 (min-max) ─────────────────────────────────────────────
def norm(series):
    mn, mx = series.min(), series.max()
    return (series - mn) / (mx - mn) if mx != mn else series * 0
 
df["n_delay"]           = norm(df["delay_sec"])
df["n_flow"]            = norm(df["total_flow"])
df["n_passenger_delay"] = norm(df["passenger_delay"])
df["n_occupancy"]       = norm(df["avg_occupancy"])
 
# ── 5. Kompozit prioritáspontszám ─────────────────────────────────────────────
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
result = df[["rank", "id", "name", "delay_str", "total_flow",
             "avg_occupancy", "passenger_delay", "priority_score"]].sort_values("rank")
print(result.rename(columns={
    "rank": "Rang", "id": "Kód", "name": "Megálló", "delay_str": "Várakozás",
    "total_flow": "Forgalom", "avg_occupancy": "Átl.telít.",
    "passenger_delay": "Személy-mp", "priority_score": "Pont"
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
    "node_rank", "name", "megallok", "osszes_jarat", "osszes_forgalom",
    "atl_varakozas", "max_varakozas", "atl_telitettseg",
    "osszes_szemelydel", "osszes_pont"
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
# ELEMZÉS 3 – Forgalmi kategóriák
# ══════════════════════════════════════════════════════════════════════════════
print()
print(SEP)
print("  3. FORGALMI KATEGÓRIÁK SZERINTI BONTÁS")
print(SEP)
 
q33 = df["total_flow"].quantile(0.33)
q66 = df["total_flow"].quantile(0.66)
 
def forgalmi_kat(f):
    if f <= q33:   return " Alacsony forgalom"
    elif f <= q66: return " Közepes forgalom"
    else:          return " Magas forgalom"
 
df["forgalmi_kat"] = df["total_flow"].apply(forgalmi_kat)
 
for kat in [" Magas forgalom", " Közepes forgalom", " Alacsony forgalom"]:
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
    magas_var  = row["delay_sec"]  > med_delay
    magas_forg = row["total_flow"] > med_flow
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
        print(f"  │  [{str(r['id']):>3}] {r['name']:<33} vár: {r['delay_str']}  "
              f"forgalom: {int(r['total_flow']):>6}  pont: {r['priority_score']:.1f}")
    print(f"  └─ Átl. pont: {sub['priority_score'].mean():.1f}  |  "
          f"Össz. személyperc-veszt.: {sub['passenger_delay'].sum():,.0f}")
    print()
 
# ══════════════════════════════════════════════════════════════════════════════
# ELEMZÉS 5 – Beavatkozási javaslatok
# ══════════════════════════════════════════════════════════════════════════════
print(SEP)
print("  5. BEAVATKOZÁSI JAVASLATOK TÍPUS SZERINT")
print(SEP)
 
def javaslat(row):
    delay = row["delay_sec"]
    flow  = row["total_flow"]
    occ   = row["avg_occupancy"]
    if delay > 300:
        return " Azonnali beavatkozás – terminál/végállomás-kezelés felülvizsgálata"
    elif occ > 30 and delay > 120:
        return " Kapacitásbővítés + menetrendgyorsítás (zsúfolt + lassú)"
    elif flow > med_flow * 2 and delay > med_delay:
        return " Forgalomtechnikai beavatkozás – jelzőlámpa-prioritás javasolt"
    elif flow > med_flow * 2:
        return " Menetrend-optimalizálás – csúcsidős sűrítés"
    elif delay > 120:
        return "  Megállókezelés gyorsítása – utas-áramlat design"
    else:
        return "Elfogadható – megfigyelés elegendő"
 
df["javaslat"] = df.apply(javaslat, axis=1)
 
for jav_tip in df["javaslat"].unique():
    sub = df[df["javaslat"] == jav_tip].sort_values("priority_score", ascending=False)
    print(f"\n  {jav_tip}")
    for _, r in sub.iterrows():
        print(f"    [{str(r['id']):>3}] {r['name']:<35} pont: {r['priority_score']:.1f}")
 
print()
print(SEP)
print(f"  Adatforrás: {CSV_PATH}  |  Betöltött megállók: {len(df)}")
print(f"  Súlyok: várakozás {W_DELAY*100:.0f}%  |  forgalom {W_FLOW*100:.0f}%  "
      f"|  személyperc {W_PDEL*100:.0f}%  |  telítettség {W_OCC*100:.0f}%")
print("  Hangolás: W_DELAY / W_FLOW / W_PDEL / W_OCC változók a script tetején.")
print(SEP)