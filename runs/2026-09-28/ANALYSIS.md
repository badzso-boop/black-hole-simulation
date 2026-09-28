# Kampány-elemzés — 2026-09-28

A számok forrása: [RESULTS.md](RESULTS.md) (automatikusan generált táblázatok),
[summary.csv](summary.csv), [results_compact.json](results_compact.json); futásonkénti
naplók: [logs/](logs/). Újrafuttatás: `python scripts/run_campaign.py` majd
`python scripts/analyze_campaign.py runs/<id>` (a szimuláció determinisztikus).

## 0. Összefoglaló

1. **A szimulátor megbízható.** 71/71 futás sikeres; mind a 7 irodalmi ellenőrzés
   teljesül; az energiamérleg legnagyobb hibája 7e-14; az eredmény 25 és 1000
   mintapont között 1e-13-on belül azonos. A 105 Rust + 22 Python teszt zöld.
2. **Egy valódi fekete lyuk ma nem párolog, hanem nő.** A határ M_eq ≈ 5.6e22 kg
   (kb. a Hold tömege): ennél nagyobb fekete lyuk a kozmikus háttérsugárzásból
   többet nyel el, mint amennyit Hawking-sugárzásként kibocsát. Minden ismert
   (csillag- és szupernagy tömegű) fekete lyuk ennél 8–17 nagyságrenddel nehezebb.
3. **A Hawking-párolgás csak primordiális fekete lyukakra számít** — és ott
   erősen függ a részecskefizikától és a forgástól (lásd 2–4.).
4. **A Norbi-hipotézis a valódi objektumokon is ugyanazt adja, mint az
   elméleti futásokon:** a bébiuniverzum létrejön és 33–77 e-redőnyit tágul, de
   kauzálisan le van választva; a külső spektrum bitre azonos a standarddal, az
   üzenet nem nyerhető vissza (0 bit, a unitér referencia 2 bitjével szemben).

## 1. Futtatás és teljesítmény

Gép: Intel i5-2500S (2011), 4 mag, 7.6 GB RAM, Debian 13.

| | Érték |
|---|---|
| 71 futás egymás után | 239 s |
| egy futás (100 mintapont) | medián 1.9 s |
| 300 mintapontos spin-futás | ~8.6 s |
| 1000 mintapont | 12.3 s |
| csúcs-RAM | 54–68 MB |
| tesztcsomag | 47 s (Rust) + 16 s (Python) |

A futási idő a mintapontok számával lineárisan nő (spektrumszámítás minden
pontban), a fizikai eredmény viszont nem változik (8e-14). A gép bőven elég;
nagy paraméter-szkennelésnél a futások párhuzamosíthatók (`--jobs N`).

## 2. Tömeg-scan: ki párolog el, és mennyi idő alatt?

| Tartomány | Mit mutat a szimuláció |
|---|---|
| 2 m_P … 1e6 kg | τ ∝ M³ pontosan (lokális kitevő 3.000): itt minden részecskefajta már „be van kapcsolva", f(M) állandó. 1 kg: 1.3e-35 Gyr = 4e-19 s. |
| 1e9 … 1e12 kg | A kitevő 3.16–3.6-ra nő: ahogy a fekete lyuk zsugorodva felmelegszik, egyre több részecske (müon, pion, kvarkok) válik kibocsáthatóvá, ami a késői párolgást gyorsítja. Ez a MacGibbon–Webber-kép jellegzetes lenyomata. |
| **5.1e11 kg** | **11.1 Gyr** — ez a „ma elpárolgó" tömeg. Az irodalmi 13.8 Gyr-hez képest 19%-kal rövidebb: a közelítő fajta-küszöbök (főleg a kvark/gluon QCD-küszöb) miatt. |
| 1e15 … 1e20 kg | Újra τ ∝ M³: itt már csak foton, graviton és neutrínó jön ki. |
| 1e22 kg (T_H = 12 K) | Még párolog, 4e32 Gyr alatt. |
| 5e22 kg (T_H = 2.45 K) | **Még párolog, pedig hidegebb a CMB-nél** — mert gravitonokat és (a legkönnyebb) neutrínókat is kibocsát, de csak fotonokat nyel el. |
| ≥ 7e22 kg | **Nő.** Az egyensúly M_eq = 5.562e22 kg (instabil). |
| M_☉ | ΔM = +1.1e4 kg 13.8 Gyr alatt (1e-26 relatív) — f64-ben a tömegből nem is látszana, az energiamérlegből pontos. Vákuumban 10 Gyr alatt −1.8e-27 kg. |

A horizonttól a belső visszapattanásig tartó sajátidő ∝ M (4GM/3c³ klasszikusan):
a Nap-tömegű fekete lyuknál 6.6 μs, egy primordiálisnál 1e-24 s.

## 3. Forgás (Kerr)

| a*₀ | τ/τ(0) teljes SM | τ/τ(0) γ+graviton |
|---|---|---|
| 0.1 | 0.992 | 0.986 |
| 0.5 | 0.865 | 0.818 |
| 0.9 | 0.542 | 0.503 |
| 0.99 | 0.410 | 0.386 |
| 0.999 | 0.387 | 0.366 |

- A forgó fekete lyuk **hidegebb** (a* = 0.999-nél T_H 12×-esen kisebb), mégis
  **gyorsabban párolog**: a forgás a szuperradiancia révén a gravitonok és fotonok
  kibocsátását nagyságrendekkel növeli (Page 1976b).
- A maximális gyorsulás 2.58× (teljes SM) ill. **2.73× (γ+graviton)**. Page a
  2.0–2.7× tartományt adja; a γ+graviton érték a felső szélén épp kilóg, ami a
  tömeges fajták közelítő Kerr-kezelése és a táblázat-interpoláció határain belül van.
- Kis spinnél (a* ≤ 0.3) a hatás < 5–8%: a spin előbb eltűnik, mint hogy a tömeg
  érdemben fogyna.
- A teljes Standard Modell kevésbé érzékeny a spinre (0.387 vs 0.366), mert a
  tömeges fajták — amelyek a teljesítmény nagy részét adják — kevésbé erősödnek.

## 4. Emissziós modell: mennyit számít a részecskefizika?

5.1e11 kg-nál: teljes SM 11.1 Gyr, foton+graviton 196 Gyr, csak fotonos fekete
test 354 Gyr — **17–32-szeres** különbség. A „ma elpárolgó" tömeg tehát
elsősorban a kibocsátható részecskék számán múlik, nem a greybody-részleteken.
A spektrális nem-termalitás mindhárom modellnél és minden tömegen 0.267: ez a
greybody-torzítás skálafüggetlen alakja, nem információ.

## 5. Környezet: ami utána beleesik

- **Aszteroida egy primordiális fekete lyukba** (1e12 kg, t = 3.2 Gyr-nél, amikor
  a lyuk már 0.99e12 kg): a tömeg megduplázódik, az élettartam 110 → **968 Gyr**
  (τ ∝ M³ miatt ~9×).
- **Két beesés** (0.5e12 kg 1.6 Gyr-nél, 2e12 kg 63 Gyr-nél): 5064 Gyr. A
  beesések „újraindítják" a párolgás óráját — a sorrend és az időzítés számít.
- **Eddington-korlátos növekedés** 10 M_☉-ről 100 Myr alatt: 7.373× (e^(t/t_S),
  t_S = 50 Myr) — ez a szupernagy fekete lyukak korai növekedésének klasszikus
  időskálája; ennyi idő alatt csak ~2 e-redő, ezért a korai Univerzum kvazárjai
  (1e9 M_☉ 700 Myr alatt) nehezebb magot vagy Eddington feletti szakaszt igényelnek.
- **Vékony korong a*=0-ból:** a spin a Thorne-határon (0.998) telítődik; a tömeg
  közben 7.7×-esére nő (a Bardeen-út √6 ≈ 2.45×-nél érné el az 1-et, a
  Thorne-korlát megállítja). A korong hatásfoka közben 5.7% → 32%.

## 6. Valódi fekete lyukak

| Objektum | Mit mutat |
|---|---|
| **Sgr A\*** | A mai rátával (7e-9 M_☉/év) 13.8 Gyr alatt +96 M_☉ (2e-5 relatív). L/L_Edd = 1.5e-9 — a Tejútrendszer központja rendkívül „éhes" és halvány. Árnyék 53.3 μas; várt gyűrű 56.4 μas, mért 51.8 ± 2.3 μas: **δ = −0.082**, pontosan az EHT által publikált −0.08 ± 0.09. |
| **M87\*** | +1.2e7 M_☉ (0.19%), a* 0.900 → 0.897 (a gömbszimmetrikus akkréció impulzusmomentum nélkül „hígítja" a spint). Várt gyűrű 42.0 μas, mért 42 ± 3: **δ = 0.000** (a tömeget az EHT éppen ebből határozta meg, így ez konzisztencia-, nem független ellenőrzés). L/L_Edd = 7e-6. |
| **Cygnus X-1** | A kísérőcsillag ~5 Myr-ében +0.01 M_☉; a spin a Thorne-határon marad, korong-hatásfok 32%, L/L_Edd = 0.02 (bemenet). Árnyéka ~0.001 μas — 4–5 nagyságrenddel az EHT felbontása alatt. |
| **GW150914 / GW250114** | Izolált maradványok: 13.8 Gyr alatt csak a CMB-ből ~4e7 kg (3.5e-25 relatív); a spin gyakorlatilag változatlan. |
| **pbh-today** | Elpárolog 11.1 Gyr alatt (lásd 2.). |

Minden valódi fekete lyuk T_H-ja 6e-18 K (M87\*) és 8e-10 K (GW-maradványok)
között van — 9–18 nagyságrenddel hidegebb a CMB-nél. A Hawking-sugárzásuk
megfigyelhetetlen, és a párolgásuk a mai Univerzumban nem indul el.

## 7. Norbi vs. Standard

Mind a 6 katalógus-objektumra:
- a **külső spektrum bitre azonos** a két módban;
- a **kauzális csatorna nem létezik** (a visszapattanás a belső horizont alatt);
- a bébiuniverzum létrejön: H_max = 1.6–1.7e43 1/s (≈ 0.93/t_P, a tömegtől
  független — ez az LQC-dinamika jellemzője), és a kezdő sugárig 33 (PBH) –
  77 (M87\*) e-redőnyit tágul;
- **információ:** Standard és Norbi 0 bit, a unitér (Page/Hayden–Preskill)
  referencia 2 bit.

A Norbi-hipotézis tehát a valódi objektumokon sem különböztethető meg kívülről
a standard képtől — ugyanaz az eredmény, mint a v3.0 elméleti futásain.

## 8. Korlátok, amik ezeket a számokat érintik

- A fajta-küszöbök közelítők: a „ma elpárolgó" PBH élettartama ~19%-kal rövid.
- Kerr: a tömeges fajták a tömegtelen mező Kerr-arányát kapják; a CMB-elnyelés
  és a belső modell a* = 0-val.
- A környezet időben állandó: a CMB nem hűl, a mai akkréciós ráta 13.8 Gyr-ig
  (Sgr A\*, M87\*) — ez „mi lenne, ha" becslés, nem kozmológiai előrejelzés.
- Sgr A\* és M87\* spinje nem mért (0.9 feltételezve).
