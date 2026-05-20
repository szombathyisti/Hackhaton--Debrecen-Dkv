Megnézem a táblát, hogy milyen oszlopok és adatok vannak benne, aztán megmondom, hogyan lehet belőle a hackathon-megoldást erősíteni.

Ennyi ideig gondolkozott: 1m 35s

Igen, nagyon is segíthet. Megnéztem az Excel fájlt: ez pont olyan adat, amiből már lehet egy hackathonos MVP-t építeni.

A táblában 705 megálló/megállóirány rekord van, 2025. januári összesített adatokkal. Van benne:

megálló azonosító és név,
tervezett megállások száma,
felszállók száma,
leszállók száma,
utasforgalom,
érkezési és indulási kihasználtság,
átlagos késés.

A késés Excel-időformátumban van, ezt percre így lehet átszámolni:

késés percben = Delay × 1440
Mire jó ez a ti ötletetekhez?

Ebből már tudtok készíteni egy első prioritási térképet.

Nem csak azt lehet megmutatni, hogy hol nagy a késés, hanem azt is, hogy hol érint sok utast a késés. Ez sokkal erősebb, mert egy 4 perces késés kevés utassal lehet kevésbé fontos, mint egy 2,5 perces késés több tízezer utassal.

Erre jó mutató lehet:

Delay Impact = utasforgalom × átlagos késés percben

Ez megmutatja, hogy hol „fáj” legjobban a késés az utasoknak.

Az adatok alapján kiemelt megállók

A legerősebb késési-hatású helyek a táblában például:

Megálló	Utaskitettség	Átlagos késés	Miért fontos?
Csokonai Színház	nagyon magas	kb. 2,4–2,6 perc	sok utast érint, erős prioritás
Nagyállomás	nagyon magas	kb. 1,5–2,7 perc	nagy csomópont, sok irány
Helyközi autóbusz-állomás	magas	kb. 1,8–2,2 perc	átszállási pont
Holló László sétány	magas	kb. 2,6–3,3 perc	jelentős késési hatás
Segner tér	magas	kb. 1,5 perc	fontos városi csomópont

Ezeket a térképen érdemes lenne piros/narancs kiemeléssel mutatni.

Hogyan illesszétek a challenge-höz?

A ti eredeti ötletetek:

ahol sokat késnek a buszok, oda buszsávot javasolnánk

Ezt így érdemes továbbfejleszteni:

ahol magas az utasforgalom, magas a késési hatás, és a megálló komfortja vagy környezete gyenge, oda célzott beavatkozást javaslunk: buszsáv, jelzőlámpa-prioritás, fedett váró, jobb utastájékoztatás vagy akadálymentesítés.

Így már nem csak forgalomtechnikai projekt, hanem Smart Public Transport Stop Index, ami pontosan illeszkedik a kiíráshoz.

Mit kell még hozzátenni az Excelhez?

Az Excel jó alap, de a challenge teljesítéséhez kellene mellé néhány plusz oszlop, akár kézzel felvéve a demo kedvéért:

Van fedett váró? igen/nem
Van ülőhely? igen/nem
Akadálymentes? 1–5
Utastájékoztatás minősége: 1–5
Menetrend olvashatósága: 1–5
Közvilágítás/biztonság: 1–5
Időjárási kitettség: 1–5
Levegőminőségi kitettség: 1–5
Van kerékpártároló vagy más közlekedési kapcsolat? igen/nem
Javasolt beavatkozás
Javasolt pontszám

A demohoz használhattok egy egyszerű indexet:

Stop Priority Score =
40% késési hatás
+ 25% utasforgalom
+ 20% komfort hiányosság
+ 10% akadálymentességi probléma
+ 5% levegő/időjárás kitettség

A végeredmény egy 0–100-as pontszám lenne minden megállóra.

Például:

Csokonai Színház
Score: 92/100
Probléma: magas utasforgalom + magas késési hatás
Javaslat: buszsáv vizsgálata, jelzőlámpa-prioritás, fedett váró, jobb utastájékoztatás
Röviden

Igen, ez az Excel kifejezetten hasznos. Ebből már meg tudjátok csinálni a projekt adatvezérelt részét:

adat → pontszám → térképes megjelenítés → fejlesztési javaslat.

A legerősebb hackathon-demó az lenne, ha a megállókat térképre rakjátok, és minden pontra megjelenítitek:

utasforgalom
átlagos késés
delay impact
komfort score
összesített prioritás
javasolt fejlesztés

Így a buszsávos ötletetek nem elveszik, hanem egy nagyobb, okosabb döntéstámogató rendszer része lesz.