# Hackhaton--Debrecen-Dkv

## DKV DEBRECEN OPED DATA

Cél: elemzés készítése és folyamatos monitorozása szoftveresen, hogy melyik szakaszt kellene meggyorsítani -> hova kellhet buszsáv
Megvalósítás: a buszstopponkénti késés kumulálása és és átlagának kiszámolása egy esetleges szenzor alapján. A szenzor mérné, hogy melyik busz késik, így vonalaknénti adatok is rendelkezésre állnak. És ahol kimagaslóan sok a késés, oda megoldási javaslatot kérni/ nyújtani.
STEP-BY-STEP:
1.azt a szenzorreendszert, amit a dkv már használ a buszmegálló trackeléséhez használatba kell venni.
1.1. Kell az adat arról, hogy mikor ér a XYZ busz a megálló közelébe, mikor mnyitja és mikor csukja az az ajtót és mikor hagyja el a buszmegálló területét
2.Kell az elvárt menetrend és az ahhoz összehasonlított késés. Ezt a szenzorral el lehet érni, csak össze kell hasonlítani, hogy mennyit késett
3.Kell adat, hogy hány ember van a járművön, ezzel priorizálni kell, hogy melyik késés a fontosabb. Például, egy 40 fős teli busz 5 perc késése mint egy majdnem üres, 4 fős busz 10 perc késése. Hisz több embert érint
4.Kell megfigyelni az összes környezeti adatot, ez már rendelkezésre áll a debreceni rendszereknek köszönhetően
5.Külső események, például, hogy van-e városi esemény (majális, debreceni fesztiválok)
6.Külső forgalom-> ha lehet trackelni
7.Útminőség megfigyelése-> megfigyelni, van e korreláció az űtminőség és késés között
8.Busz jelenlegi állapota, mikor volt szervízbe, milyen lehet a motor állapota, kerekek kopása
9.A megfigyelések időpontját is fel kell jegyzeni, hogy tudjuk, időre korrelál-e egy-egy késés. Ha például csak 8órakkor késik egy busz, de mindig csak akkor, az a reggeli forgalomnak köszönhető
