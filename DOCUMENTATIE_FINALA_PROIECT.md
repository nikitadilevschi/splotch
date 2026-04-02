# SPLOTCH - Joc de Platformă de Precizie
## Documentație Tehnică Finală - Proiect de Licență

**Autor:** [Nume Student]  
**Data:** Aprilie 2026  
**Instituție:** [Universitate]  
**Programul de Studii:** [Inginerie Software/Informatică]

---

## CUPRINS

1. [Introducere](#introducere)
2. [Descrierea Proiectului](#descrierea-proiectului)
3. [Arhitectura Sistemului](#arhitectura-sistemului)
4. [Categorii și Mecanici de Joc](#categorii-și-mecanici-de-joc)
5. [Sistem de Palete de Culori](#sistem-de-palete-de-culori)
6. [Implementare Tehnică](#implementare-tehnică)
7. [Structura Fișierelor](#structura-fișierelor)
8. [Mecanici de Joc Detaliate](#mecanici-de-joc-detaliate)
9. [Sistemul de Nivele](#sistemul-de-nivele)
10. [Concluzii și Perspective Viitoare](#concluzii-și-perspective-viitoare)

---

## INTRODUCERE

### 1.1 Motivație și Obiective

Splotch este un joc de platformă de precizie dezvoltat în Python cu ajutorul bibliotecii Pygame. Proiectul a fost conceput cu scopul de a demonstra cunoștințele în domeniul dezvoltării jocurilor, gestionării stării aplicației, și a designului interfețelor grafice interactive.

**Obiectivele principale ale proiectului:**
- Implementarea unui motor de joc funcțional cu fizică realistă
- Crearea unui sistem de nivele modular și extensibil
- Dezvoltarea unui sistem de tematizare visual coheziv
- Implementarea mecanicilor complexe de platformă și platforme mobile
- Crearea unei experiențe de joc challenging și plăcute

### 1.2 Tehnologii Utilizate

- **Limbaj de Programare:** Python 3.13
- **Biblioteci Grafice:** Pygame
- **Formaturi de Stocare:** JSON (salvare progres)
- **Sisteme de Operare:** Windows, Linux, macOS

---

## DESCRIEREA PROIECTULUI

### 2.1 Concept General

Splotch este un joc de platformă unde jucătorul trebuie să traverseze nivele pline de pericole (decupări, tăieturi cu ferăstrău, blocuri mobile). Jocul este împărțit în 5 categorii, fiecare cu 3 nivele de dificultate progresivă.

### 2.2 Mecanica Principală

Jucătorul controlează o figură pătrată care trebuie să:
- Sară peste obstacole
- Evite platformele care se mișcă sau cad
- Evite ghilotine și ferăstraie rotative
- Atingă steagul de victorie pentru a completa nivelul

### 2.3 Sisteme de Progresie

- **Sistem de Salvare:** Progresul este salvat automat în `save.json`
- **Deblocarea Categoriilor:** Categoriile se deblochează progresiv
- **Contor de Decese:** Urmărește numărul total de momente în care jucătorul a murit
- **Indicatori de Progres:** Steaguri care indică nivelele completate

---

## ARHITECTURA SISTEMULUI

### 3.1 Diagramă de Flux al Aplicației

```
Pornire Aplicație
       ↓
Inițializare Motor Pygame
       ↓
Încărcare Salvare (save.json)
       ↓
Selectare Categorie
       ↓
Selectare Nivel
       ↓
Inițializare Nivel
       ↓
Buclă de Joc (Update/Render)
       ↓
Detectare Condiții Sfâșit
       ↓
Returnare la Meniu
```

### 3.2 Structura Modulară

Proiectul este organizat în următoarele module principale:

```
splotch/
├── core/                 # Funcționalități de bază
│   ├── constants.py      # Constante și palete de culori
│   ├── save_manager.py   # Gestionarea salvării
│   └── __init__.py
├── engine/              # Motor de joc
│   ├── physics.py       # Calcule de fizică
│   ├── mblock.py        # Blocuri mobile
│   ├── spike.py         # Obstacole cu tăieturi
│   ├── sensor.py        # Senzori de activare
│   ├── tl_runner.py     # Executor de timeline
│   └── __init__.py
├── levels/              # Definiții de nivele
│   ├── builder.py       # Constructor de nivele
│   ├── platforms.py     # Nivelele Platforms
│   ├── gaps.py          # Nivelele Gaps
│   ├── spikes.py        # Nivelele Spikes
│   ├── saws.py          # Nivelele Saws
│   ├── push.py          # Nivelele Push
│   └── __init__.py
├── scenes/              # Scene de aplicație
│   ├── category_select.py   # Selectarea categoriei
│   ├── level_select.py      # Selectarea nivelului
│   ├── level_scene.py       # Scena de joc
│   └── __init__.py
├── ui/                  # Interfață grafică
│   ├── draw_helpers.py  # Funcții de desenare
│   ├── hud.py           # Head-up display
│   └── __init__.py
├── main.py             # Punct de intrare
├── splotch.py          # Clasă aplicație principală
└── save.json           # Fișier de salvare
```

### 3.3 Modelul de Scene

Aplicația funcționează pe un model de scene:
- **CategorySelectScene:** Selectarea categoriei
- **LevelSelectScene:** Selectarea nivelului din categorie
- **LevelScene:** Scena de joc cu gameplay activ

---

## CATEGORII ȘI MECANICI DE JOC

### 4.1 Cinci Categorii Principale

#### 4.1.1 GAPS (Decupări)

**Descriere:** Platforme care cad și forțează jucătorul să sară peste prapastii

**Mecanica:**
- Platforme care se prăbușesc sub greutatea jucătorului
- Jucătorul trebuie să sară înainte ca platforma să cadă
- Dificultate progresivă: decupări din ce în ce mai mari

**Implementare:**
```python
'traps': [
    dict(kind='mblock', x=544, y=320, w=96, h=160,
         sensor=(560, 192, 32, 128),
         steps=[dict(ty=6, t=0.3)], loop=False, auto=False)
]
```

#### 4.1.2 SPIKES (Ghilotine/Tăieturi)

**Descriere:** Obstacole ascunzute care se ridică din platformă când jucătorul se apropie

**Mecanica:**
- Tăieturi care se ascund în platformă
- Se activează când jucătorul se apropie (pe baza unui senzor)
- Contact = moarte instantanee

**Detectare:**
```python
if pr.colliderect(sp.kill_rect()):
    self._die()
    return
```

#### 4.1.3 PUSH (Blocuri Mobile Orizontale)

**Descriere:** Blocuri care se mișcă orizontal, empingând jucătorul

**Mecanica:**
- Blocuri care se mișcă în direcții specificate
- Pot deplasa jucătorul dacă este pe ele
- Contactul din laterale = moarte prin zdrobire

#### 4.1.4 PLATFORMS (Platforme Mobile Verticale)

**Descriere:** Platforme care se ridică și coboară

**Mecanica:**
- Platforme care se deplasează pe verticală
- Jucătorul poate fi zdrobit dacă este prins între ele
- Detectare crush: când jucătorul este complet înclus în interiorul unei platforme

**Detectare Zdrobire:**
```python
if mr.top < pr.top and mr.bottom > pr.bottom:
    # Jucator zdrobit
    self._die()
    return
```

#### 4.1.5 SAWS (Ferăstraie)

**Descriere:** Discuri rotative cu dinți care se mișcă pe platformă

**Mecanica:**
- Ferăstraie care se rotesc continuu
- Se mișcă pe platforme sau spații deschise
- Contactul = moarte instantanee

---

## SISTEM DE PALETE DE CULORI

### 5.1 Concepție și Implementare

Un sistem inovator de tematizare vizuală a fost implementat pentru a asigura coerență vizuală în fiecare categorie.

### 5.2 Structura Paletei

Fiecare categorie are o paletă cu 5 culori:

```python
CAT_PALETTES = [
    # Categoria 0: GAPS (Teal)
    {
        'primary':    (70, 180, 168),      # Culoare fundal
        'dark':       (45, 130, 120),      # Platforme și dale
        'light':      (100, 210, 200),     # Accente
        'accent':     (120, 230, 220),     # Elemente UI
        'spike':      (160, 160, 160),     # Tăieturi
    },
    # Categoria 1: SPIKES (Roșu)
    {
        'primary':    (185, 75, 75),
        'dark':       (140, 50, 50),
        'light':      (220, 100, 100),
        'accent':     (240, 130, 130),
        'spike':      (200, 100, 100),
    },
    # ... alte categorii
]
```

### 5.3 Aplicare Dinamică

Paleta este aplicată din urmă în urmă pe tot ecranul jocului:

**Locuri de Aplicare:**
- Fundal joc (culoare primară)
- Dale și platforme (culoare întunecată)
- Bară de top (culoare întunecată)
- Elemente UI (culori accent)
- Card-uri de victorie (teme categorie)
- Indicatori de progres (culori accent)

### 5.4 Funcția de Recuperare Paletă

```python
def get_category_palette(category_index):
    """Obține paleta de culori pentru o categorie dată."""
    if 0 <= category_index < len(CAT_PALETTES):
        return CAT_PALETTES[category_index]
    return CAT_PALETTES[0]  # Implicit teal
```

---

## IMPLEMENTARE TEHNICĂ

### 6.1 Motorul de Fizică

#### 6.1.1 Gravitație și Cădere

```python
self.vy += dt * 800  # Accelerație gravitație
self.y += self.vy * dt

# Limita vitezei de cădere
if self.vy > 800:
    self.vy = 800
```

#### 6.1.2 Detecția Coliziunilor

Coliziunile sunt detectate prin verificarea suprapunerii dreptunghiurilor:

```python
if player_rect.colliderect(platform_rect):
    # Rezolvare coliziune
    if player_vy > 0:  # Cădere
        player.y = platform.top - player.height
        player.vy = 0
```

#### 6.1.3 Platforme Mobile

Platformele mobile sunt controlate prin timeline-uri:

```python
class TLRunner:
    def __init__(self, x, y, steps, loop=False):
        self.x = x
        self.y = y
        self.steps = steps  # Lista de pași de animație
        self.loop = loop
    
    def update(self, dt):
        # Actualizare poziție pe baza timeline-ului
        if self.t >= self.step_duration:
            self.advance_step()
```

### 6.2 Sistemul de Senzori

Senzorii sunt folosiți pentru a activa platformele mobile:

```python
class Sensor:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
    
    def check(self, player_rect):
        """Verifică dacă jucătorul este în senzor."""
        return self.rect.colliderect(player_rect)
```

### 6.3 Sistemul de Salvare

Progresul este salvat în JSON:

```json
{
    "deaths": 41,
    "unlocked_cats": [0, 1, 2, 3],
    "unlocked_lvls": {
        "0": [0, 1, 2],
        "1": [0, 1, 2],
        "2": [0]
    },
    "completed": {
        "0_0": true,
        "0_1": true,
        "0_2": true
    }
}
```

---

## STRUCTURA FIȘIERELOR

### 7.1 Fișiere Principale

#### 7.1.1 main.py
Punct de intrare al aplicației. Inițializează Pygame și pornește ciclu principal.

#### 7.1.2 splotch.py
Clasă principală Game care gestionează scene și tranziții.

#### 7.1.3 core/constants.py
Constante globale: dimensiuni ecran, culori, palete, nume categorii.

#### 7.1.4 core/save_manager.py
Funcții pentru încărcare și salvare a progresului din/în JSON.

### 7.2 Module de Joc

#### 7.2.1 engine/physics.py
Clasa Player cu fizică, coliziuni, și mișcare.

#### 7.2.2 engine/mblock.py
Clasă MBlock pentru platforme mobile cu timeline-uri.

#### 7.2.3 engine/spike.py
Clasă SpikeObj pentru tăieturi ascunse și mobile.

#### 7.2.4 engine/sensor.py
Clasa Sensor pentru detectarea prezenței jucătorului.

### 7.3 Definiri de Nivele

#### 7.3.1 levels/gaps.py, platforms.py, spikes.py, etc.
Definiții de nivele în format dictionar cu:
- `tiles`: Tablou 2D al platformei
- `traps`: Lista de pericole
- `player`: Poziție inițială
- `goal`: Poziție steag
- `hint`: Indiciu pentru jucător

---

## MECANICI DE JOC DETALIATE

### 8.1 Sistem de Moarte

Jucătorul poate muri din mai multe cauze:

**8.1.1 Cădere**
```python
if p.y > OH + 80:
    self._die()
```

**8.1.2 Contact cu Tăieturi**
```python
for sp in self._spikes:
    if pr.colliderect(sp.kill_rect()):
        self._die()
```

**8.1.3 Zdrobire între Platforme**
```python
for mb in self._mblocks:
    if mr.top < pr.top and mr.bottom > pr.bottom:
        # Jucator complet închis în platformă
        self._die()
```

**8.1.4 Contact cu Ferăstraie**
```python
for mb in self._mblocks:
    if mb.is_saw and check_saw_collision(pr, mb.rect):
        self._die()
```

### 8.2 Sistem de Recompense

- **Fiecare nivel completat:** Steagul se marchează ca complet
- **Toate nivelele dintr-o categorie:** Categoria se marchează complet
- **Categoria completă:** Deblochează categoria următoare
- **Contor de decese:** Urmărește performanța totală

### 8.3 Mecanica "Carry Player"

Jucătorul care stă pe o platformă mobilă este transportat cu ea:

```python
def _carry_player_with_moving_blocks(self, p, pr):
    for mb in self._mblocks:
        if pr.colliderect(mb.rect):
            dx = mb.rect.x - mb.prev_rect.x
            dy = mb.rect.y - mb.prev_rect.y
            p.x += dx
            p.y += dy
```

---

## SISTEMUL DE NIVELE

### 9.1 Format de Definiție

Fiecare nivel este definit ca dicționar Python:

```python
LEVEL_NAME = {
    'tiles': [matriz_27x15_cu_1=platform_0=gol],
    'player': [x, y],
    'goal': [x, y],
    'traps': [list_de_blockuri_mobile],
    'hint': "Indiciu pentru jucător"
}
```

### 9.2 Tabloul de Dale

Tabloul 2D este liniarizat într-o listă de 27×15 = 405 elemente:
- `1` = Dale solide (platformă)
- `0` = Spațiu gol

### 9.3 Progresie de Dificultate

**Nivel 1:** Introducere ușoară la mecanica categoriei
**Nivel 2:** Combinare de mecanici, dificultate medie
**Nivel 3:** Challenge complex, dificultate înaltă

---

## CONCLUZII ȘI PERSPECTIVE VIITOARE

### 10.1 Realizări

✅ Joc de platformă complet funcțional  
✅ 5 categorii cu 3 nivele fiecare (15 nivele total)  
✅ Sistem de fizică și coliziuni robust  
✅ Sistemul de palete de culori inovator  
✅ Progresie și salvare persistentă  
✅ Interfață grafică polisată și profesională  

### 10.2 Implementări Viitoare

1. **Nivel de Dificultate Dinamic**
   - Ajustarea vitezelor pe baza performanței
   - Nivele bonusAnonymous

2. **Editor de Nivele**
   - Instrument pentru crearea de nivele custom
   - Export/Import de nivele

3. **Multiplayer Online**
   - Tabele de clasament online
   - Competiții mondiale

4. **Elemente Grafice Avansate**
   - Animații de particulă
   - Efecte de shader
   - Teme cu gradient

5. **Sunet și Muzică**
   - Audio spatialized 3D
   - Muzică de fundal dinamică
   - Efecte sonore pentru fiecare acțiune

6. **Sistem de Achievement-uri**
   - Realizări deblocabile
   - Badges de performanță
   - Provocări zilnice

### 10.3 Concluzii Finale

Splotch demonstrează o înțelegere solidă a:
- Dezvoltării jocurilor în Python
- Designului arhitecturii software
- Gestionării stării aplicației
- Creării experiențelor utilizator engaging
- Implementării sistemelor complexe de fizică

Proiectul servește ca punct de plecare solid pentru dezvoltarea unui motor de joc mai avansat și ar putea fi extins cu funcționalități suplimentare.

---

## REFERINȚE

- Documentația Pygame: https://www.pygame.org/docs/
- Python Official Documentation: https://docs.python.org/3/
- Game Programming Patterns: https://gameprogrammingpatterns.com/

---

**Document Finalizat:** Aprilie 2026  
**Status:** Complet și Verificat  
**Versiune:** 1.0 - Finală

