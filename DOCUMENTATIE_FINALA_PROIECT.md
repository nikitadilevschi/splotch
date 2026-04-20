# RAGE BAIT
## Documentatie tehnica finala - Proiect de licenta

**Autor:** [Nume Student]  
**Coordonator:** [Nume Coordonator]  
**Institutie:** [Universitate]  
**Program de studii:** [Informatica / Inginerie Software]  
**Data:** Aprilie 2026  
**Versiune aplicatie:** 1.3.0

---

## Cuprins

1. Introducere
2. Obiective si cerinte
3. Tehnologii utilizate
4. Arhitectura aplicatiei
5. Structura proiectului
6. Modelul datelor de nivel
7. Mecanici si subsisteme de joc
8. Persistenta datelor (save system)
9. Interfata utilizator si UX
10. Testare si validare
11. Limitari cunoscute
12. Concluzii si directii viitoare
13. Bibliografie

---

## 1. Introducere

**Rage Bait** este un joc 2D de tip precision platformer dezvoltat in Python folosind biblioteca Pygame. Proiectul are scop educational si demonstreaza competente de arhitectura software, modelare a starii aplicatiei, implementare de fizica 2D si design modular orientat pe extensibilitate.

Tema centrala a jocului este traversarea unor niveluri cu obstacole dinamice, in care succesul depinde de timing, control precis si intelegerea pattern-urilor de miscare ale capcanelor.

---

## 2. Obiective si cerinte

### 2.1 Obiective principale

- Implementarea unui gameplay fluid la 60 FPS, cu input responsive.
- Organizarea codului pe module independente (core, engine, levels, scenes, ui).
- Definirea nivelurilor intr-un format declarativ, usor de extins.
- Integrarea unui sistem de progres persistent (salvare automata).
- Dezvoltarea unei identitati vizuale coerente prin palete de culori pe categorie.
- Integrarea unui subsistem audio complet (muzica, efecte, mute persistent).

### 2.2 Cerinte functionale

- Selectare categorie si nivel prin scene separate.
- Simulare fizica pentru jucator (gravitate, saritura, coliziuni).
- Capcane cu activare conditionata (senzori) si miscari pe timeline.
- Teleportoare cu destinatii multiple si mod "self_top".
- Contorizare decese totale si per nivel.
- Deblocare progresiva a continutului.

### 2.3 Cerinte non-functionale

- Cod modular si lizibil pentru prezentare academica.
- Timpi de raspuns buni pe sisteme desktop obisnuite.
- Compatibilitate minima: Python 3.10+ (dezvoltat/testat pe 3.13).
- Mentinerea starii intre sesiuni prin JSON.

---

## 3. Tehnologii utilizate

- **Limbaj:** Python
- **Framework multimedia:** Pygame
- **Persistenta:** JSON (`save.json`)
- **Gestionare dependinte:** `pip` + `requirements.txt`
- **Control versiuni:** Git / GitHub

Motivatie tehnologica: stack-ul Python + Pygame permite dezvoltare rapida, cod usor de explicat intr-un context universitar si control direct asupra buclei de joc.

---

## 4. Arhitectura aplicatiei

Aplicatia foloseste o arhitectura de tip **scene-based**, coordonata de clasa `Game` din `main.py`.

Flux general:

1. Initializare Pygame, fereastra, ceas, salvare.
2. Afisare scena de selectie categorie.
3. Selectie nivel.
4. Initializare scena gameplay.
5. Bucla de joc: `handle_event -> update -> draw`.
6. Tranzitii intre scene in functie de actiuni/stare.

### 4.1 Scene principale

- `CategorySelectScene` - selectie categorie
- `LevelSelectScene` - selectie nivel in categorie
- `LevelScene` - logica gameplay, coliziuni, capcane, win/death

### 4.2 Separarea responsabilitatilor

- **core/**: constante, salvare, audio
- **engine/**: fizica, capcane, senzori, timeline
- **levels/**: definitii de nivele + builder
- **scenes/**: managementul starii de joc
- **ui/**: functii de desen si HUD

Aceasta separare reduce cuplarea, creste mentenabilitatea si sustine extinderea (noi mecanici / noi categorii).

---

## 5. Structura proiectului

```text
splotch/
├── main.py
├── core/
│   ├── constants.py
│   ├── save_manager.py
│   └── sound_manager.py
├── engine/
│   ├── physics.py
│   ├── mblock.py
│   ├── spike.py
│   ├── teleporter.py
│   ├── sensor.py
│   └── tl_runner.py
├── levels/
│   ├── builder.py
│   ├── gaps.py
│   ├── spikes.py
│   ├── push.py
│   ├── platforms.py
│   ├── saws.py
│   ├── controls.py
│   ├── teleporters.py
│   └── __init__.py
├── scenes/
│   ├── category_select.py
│   ├── level_select.py
│   └── level_scene.py
├── ui/
│   ├── draw_helpers.py
│   └── hud.py
├── assets/
│   ├── images/
│   └── sounds/
├── save.json
└── README.md
```

Date curente joc (v1.3.0):

- **7 categorii**
- **21 niveluri** (3 niveluri/categorie)

Categorii: `Gaps`, `Spikes`, `Push`, `Platforms`, `Saws`, `Controls`, `Teleporters`.

---

## 6. Modelul datelor de nivel

Un nivel este definit ca dictionar Python in modulele din `levels/`.

Structura uzuala:

```python
LEVEL_X = {
    'tiles': [...],            # grid 27x15, valori 0/1
    'player': [x, y],          # spawn jucator
    'goal': [x, y],            # pozitie steag
    'traps': [...],            # capcane (mblock/spike/teleporter)
    'hint': 'text optional',
}
```

Campuri extinse folosite in v1.3.0:

- `goal_trigger`: muta steagul cand jucatorul atinge un senzor
- `max_fall`: plafon local pentru viteza de cadere
- `reversed_tiles`: zone cu control inversat
- `jump_boost_tiles`: placi cu saritura imbunatatita

### 6.1 Constructorul de capcane

`levels/builder.py` foloseste `_build_trap(td)` pentru a construi obiecte runtime in functie de `kind`:

- `mblock` -> `MBlock`
- `spike` -> `SpikeObj`
- `teleporter` -> `Teleporter`

Pentru teleporter sunt suportate:

- destinatie unica (`dest_x`, `dest_y`)
- destinatii multiple (`destinations`)
- modul `self_top` (teleport pe verticala deasupra portalului curent)
- activare prin senzor
- cooldown configurabil

---

## 7. Mecanici si subsisteme de joc

### 7.1 Fizica jucatorului

`engine/physics.py` gestioneaza:

- gravitatia
- saritura
- coliziunea cu platforme
- coyote time si jump buffering (control mai permissiv)

Parametri principali (din `core/constants.py`):

- `GRAVITY = 1400`
- `MAX_FALL = 850`
- `JUMP_V = -420`
- `SPEED = 210`

### 7.2 Timeline runner pentru miscari

`engine/tl_runner.py` interpreteaza pasi de animatie pe baza de timp:

- `tx` / `ty` = deplasare in multipli de tile
- `t` = durata
- `d` = delay optional
- `e` = easing (`ease-in`, `ease-out`, `ease-in-out`)

Format recomandat al pasilor:

```python
steps = [
    {'tx': 2.0, 't': 0.6},
    {'ty': -1.0, 't': 0.4, 'e': 'ease-out'},
]
```

### 7.3 Obstacole si evenimente

- **MBlock**: blocuri mobile, inclusiv mod saw
- **SpikeObj**: capcane tip spikes
- **Teleporter**: transport instant pe destinatie
- **Sensor**: activare conditionata pentru capcane/obiective

### 7.4 Reguli de moarte si victorie

Conditii principale de moarte:

- cadere sub lumea de joc
- coliziune cu spike
- coliziune cu saw
- zdrobire de bloc mobil

Conditie de victorie:

- jucatorul intersecteaza `goal_rect`

La victorie:

- nivelul este marcat completat
- se deblocheaza urmatorul nivel
- la completarea categoriei se deblocheaza categoria urmatoare

---

## 8. Persistenta datelor (save system)

Persistenta este implementata in `core/save_manager.py`.

Modelul de salvare include:

```json
{
  "deaths": 0,
  "level_deaths": {},
  "completed": {},
  "unlocked_cats": [0, 1],
  "unlocked_lvls": {
    "0": [0], "1": [0], "2": [0],
    "3": [0], "4": [0], "5": [0], "6": [0]
  },
  "muted": false
}
```

Caracteristici:

- compatibilitate cu salvari mai vechi prin backfill de chei lipsa
- salvare automata la evenimente relevante (moarte, win, mute)
- statistici separate total/per nivel

---

## 9. Interfata utilizator si UX

### 9.1 Sistem vizual pe palete

`core/constants.py` defineste `CAT_PALETTES`, cate una pentru fiecare categorie. Paleta este folosita pentru:

- fundal si tile-uri
- accent UI
- card de level complete
- elemente HUD

### 9.2 HUD si feedback

`scenes/level_scene.py` + `ui/draw_helpers.py` afiseaza:

- top bar cu nivel curent
- buton back
- progres pe cele 3 niveluri ale categoriei
- contor decese per nivel
- buton mute
- hint-uri contextuale
- overlay de moarte / victorie

### 9.3 Audio

`core/sound_manager.py` gestioneaza:

- muzica de fundal
- efecte jump/death/win
- mute/unmute global cu persistenta in salvare

---

## 10. Testare si validare

Testarea a fost realizata predominant manual, orientata pe functionalitate si regresii:

- verificare tranzitii intre scene
- verificare coliziuni si fizica pe fiecare categorie
- verificare activare senzori si secvente timeline
- verificare teleportoare (destinatii multiple + self_top)
- verificare salvare/incarcare progres
- verificare comportament audio si mute persistent

### 10.1 Scenarii de regresie recomandate

1. Pornire joc nou si verificare deblocari initiale.
2. Finalizarea unui nivel si verificare `completed`/`unlocked_lvls`.
3. Moarte repetata si verificare crestere `deaths` + `level_deaths`.
4. Test pentru niveluri cu senzori, inclusiv teleporter activat conditionat.
5. Test pentru limite de nivel (anti-teleport in afara lumii).

---

## 11. Limitari cunoscute

- Testare automata limitata (proiect orientat gameplay real-time).
- Dependenta directa de Pygame pentru randare/input/audio.
- Echilibrarea dificultatii se face manual (fara instrument de analytics).
- Fara editor intern de nivel in versiunea curenta.

---

## 12. Concluzii si directii viitoare

### 12.1 Concluzii

Proiectul valideaza implementarea unui joc 2D complet functional, cu arhitectura modulara, mecanici variate si persistenta robusta. Sistemul este suficient de flexibil pentru extindere si este adecvat pentru sustinere academica datorita separarii clare a responsabilitatilor.

### 12.2 Directii de dezvoltare

- editor vizual de niveluri
- sistem de achievement-uri
- replay/speedrun mode
- leaderboard online
- extinderea setului de mecanici (ex. trigger chaining avansat)
- testare automata partiala pentru logica non-grafica

---

## 13. Bibliografie

1. Documentatia oficiala Pygame - https://www.pygame.org/docs/
2. Documentatia oficiala Python - https://docs.python.org/3/
3. Nystrom, R. - *Game Programming Patterns*, https://gameprogrammingpatterns.com/

---

**Status document:** final tehnic (pentru prezentare universitara)  
**Ultima actualizare:** Aprilie 2026  
**Versiune document:** 1.3.0
