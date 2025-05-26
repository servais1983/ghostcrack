![image](https://github.com/user-attachments/assets/626e07d0-9a12-448e-bf50-5fb1b95f2d94)


# GhostCrack CLI – Brute-Force Moderne et Intelligent

**GhostCrack** est un outil CLI modulaire et extensible permettant d'effectuer des attaques par force brute éthiques dans un cadre professionnel (pentest, red team). Il supporte plusieurs protocoles, l'export JSON/PDF, les proxies, la détection de blocage, et intègre une base IA pour la prédiction de mots de passe.

---

## Sommaire

- [Structure du Projet](#structure-du-projet)  
- [Fonctionnalités Clés](#fonctionnalités-clés)  
- [Protocoles Supportés](#protocoles-supportés)  
- [Installation](#installation)  
- [Exemples d'Utilisation](#exemples-dutilisation)  
- [Export des Résultats](#export-des-résultats)  
- [Modules IA et Générateurs](#modules-ia-et-générateurs)  
- [Roadmap](#roadmap)  
- [Crédits](#crédits)

---

## Structure du Projet

```
ghostcrack/
├── cli.py
├── core/
│   ├── engine.py
│   └── protocols/
│       ├── ssh.py
│       ├── http.py
│       ├── ftp.py
│       ├── smtp.py
│       └── rdp.py
├── utils/
│   ├── wordlist.py
│   ├── logger.py
│   ├── export.py
│   ├── detection.py
│   └── generator.py
├── ai/
│   └── password_predictor.py
├── requirements.txt
└── README.md
```

---

## Fonctionnalités Clés

- Multi-threading pour rapidité maximale  
- Support complet des protocoles SSH, HTTP, FTP, SMTP, RDP  
- Support de proxy HTTP et SOCKS5  
- Export JSON et PDF  
- Détection de bannissement, blocage IP, MFA  
- Générateur intelligent de mots de passe  
- Prédiction IA (scoring de mot de passe probable)  
- Architecture modulaire et personnalisable

---

## Protocoles Supportés

| Protocole | Statut | Authentification          |  
|-----------|--------|---------------------------|  
| SSH       | Stable | Nom d'utilisateur/mot de passe |  
| HTTP      | Stable | HTTP Basic Auth           |  
| FTP       | Stable | Connexion standard        |  
| SMTP      | Beta   | AUTH LOGIN/PLAIN          |  
| RDP       | Alpha  | Interface via rdesktop (à étendre) |

---

## Installation

```bash  
git clone https://github.com/servais1983/ghostcrack  
cd ghostcrack  
pip install -r requirements.txt
```

---

## Exemples d'Utilisation

```bash
# SSH bruteforce  
python cli.py --target 192.168.1.10 --protocol ssh --user admin --wordlist rockyou.txt --threads 10 --export results.json

# HTTP avec proxy SOCKS5  
python cli.py --target example.com --protocol http --user admin --wordlist pass.txt --proxy socks5://127.0.0.1:9050

# FTP avec export PDF  
python cli.py --target ftp.host --protocol ftp --user admin --wordlist pass.txt --export report.pdf
```

---

## Export des Résultats

- **results.json** : brute export JSON
- **report.pdf** : export PDF via ReportLab

```python
# utils/export.py  
from reportlab.pdfgen import canvas

def export_pdf(results, path):  
    c = canvas.Canvas(path)  
    c.drawString(100, 800, "GhostCrack Results")  
    y = 780  
    for r in results:  
        c.drawString(100, y, str(r))  
        y -= 15  
    c.save()
```

---

## Modules IA et Générateurs

**Prédicteur IA (ai/password_predictor.py)**

```python
from sklearn.feature_extraction.text import CountVectorizer  
from sklearn.naive_bayes import MultinomialNB

class PasswordPredictor:  
    def __init__(self):  
        self.vectorizer = CountVectorizer(analyzer='char', ngram_range=(2, 3))  
        self.classifier = MultinomialNB()

    def train(self, passwords, labels):  
        X = self.vectorizer.fit_transform(passwords)  
        self.classifier.fit(X, labels)

    def predict_score(self, password):  
        X = self.vectorizer.transform([password])  
        return self.classifier.predict_proba(X)[0]
```

**Générateur de Combinaisons (utils/generator.py)**

```python
def generate_combinations(base, patterns=["123", "!", "2025"]):  
    combos = []  
    for suffix in patterns:  
        combos.append(base + suffix)  
        combos.append(base.capitalize() + suffix)  
    return combos
```

---

## Roadmap

| Fonctionnalité | Statut |
|----------------|--------|
| Support complet RDP (rdesktop/lib) | En cours |
| GraphQL brute-force | À venir |
| Détection avancée (honeypots) | En cours |
| IA renforcée (deep learning) | À venir |
| Export HTML interactif | À venir |
| Intégration CI/CD + API | En cours |

---

## Crédits

Développé par [Servais] pour usage légal et professionnel.  
Inspiré par THC-Hydra, Medusa, et les besoins modernes en sécurité offensive.

---

## Licence

MIT – Utilisation libre pour usage éthique, recherche, et sécurité défensive.
