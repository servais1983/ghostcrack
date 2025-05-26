
![image](https://github.com/user-attachments/assets/74a48481-8af3-49e0-93ad-0470b894d1c1)

<div align="center">
  <h1>GhostCrack CLI</h1>
  <p><em>Brute-Force Moderne et Intelligent</em></p>
  
  <p>
    <a href="https://github.com/servais1983/ghostcrack/blob/main/LICENSE"><img src="https://img.shields.io/badge/Licence-MIT-blue.svg" alt="Licence MIT"/></a>
    <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.6+-blue.svg" alt="Python 3.6+"/></a>
    <a href="https://github.com/servais1983/ghostcrack/releases"><img src="https://img.shields.io/badge/Version-0.1.0-brightgreen.svg" alt="Version 0.1.0"/></a>
    <a href="https://github.com/servais1983/ghostcrack/issues"><img src="https://img.shields.io/github/issues/servais1983/ghostcrack" alt="Issues"/></a>
    <a href="#"><img src="https://img.shields.io/badge/Plateforme-Linux%20%7C%20macOS-lightgrey" alt="Plateforme"/></a>
  </p>
</div>

## 📋 Sommaire

- [📖 À propos](#-à-propos)
- [🔧 Structure du Projet](#-structure-du-projet)
- [✨ Fonctionnalités Clés](#-fonctionnalités-clés)
- [🔌 Protocoles Supportés](#-protocoles-supportés)
- [📥 Installation](#-installation)
- [🚀 Exemples d'Utilisation](#-exemples-dutilisation)
- [📊 Export des Résultats](#-export-des-résultats)
- [🧠 Modules IA et Générateurs](#-modules-ia-et-générateurs)
- [🛣️ Roadmap](#️-roadmap)
- [👨‍💻 Crédits](#-crédits)
- [📜 Licence](#-licence)

## 📖 À propos

**GhostCrack** est un outil CLI modulaire et extensible permettant d'effectuer des attaques par force brute éthiques dans un cadre professionnel (pentest, red team). Il supporte plusieurs protocoles, l'export JSON/PDF, les proxies, la détection de blocage, et intègre une base IA pour la prédiction de mots de passe.

## 🔧 Structure du Projet

```
ghostcrack/
├── cli.py                 # Point d'entrée principal
├── core/                  # Moteur principal
│   ├── engine.py          # Logique centrale
│   └── protocols/         # Implémentation des protocoles
│       ├── ssh.py         # Module SSH
│       ├── http.py        # Module HTTP
│       ├── ftp.py         # Module FTP
│       ├── smtp.py        # Module SMTP
│       └── rdp.py         # Module RDP
├── utils/                 # Utilitaires
│   ├── wordlist.py        # Gestion des listes de mots
│   ├── logger.py          # Journalisation
│   ├── export.py          # Export des résultats
│   ├── detection.py       # Détection de blocage
│   └── generator.py       # Générateur de mots de passe
├── ai/                    # Modules d'intelligence artificielle
│   └── password_predictor.py  # Prédicteur de mots de passe
├── requirements.txt       # Dépendances
└── README.md              # Documentation
```

## ✨ Fonctionnalités Clés

- ⚡ **Multi-threading** pour rapidité maximale
- 🔄 **Support complet** des protocoles SSH, HTTP, FTP, SMTP, RDP
- 🔒 **Support de proxy** HTTP et SOCKS5
- 📊 **Export JSON et PDF** des résultats
- 🛡️ **Détection** de bannissement, blocage IP, MFA
- 🔑 **Générateur intelligent** de mots de passe
- 🧠 **Prédiction IA** (scoring de mot de passe probable)
- 🧩 **Architecture modulaire** et personnalisable

## 🔌 Protocoles Supportés

<div align="center">
  <img src="https://raw.githubusercontent.com/servais1983/ghostcrack/main/assets/protocol_icons.png" alt="Protocoles supportés" width="600"/>
</div>

| Protocole | Statut | Authentification | Icône |
|:--------:|:------:|:----------------:|:-----:|
| SSH | ✅ Stable | Nom d'utilisateur/mot de passe | <img src="https://img.shields.io/badge/SSH-22-brightgreen" alt="SSH"/> |
| HTTP | ✅ Stable | HTTP Basic Auth | <img src="https://img.shields.io/badge/HTTP-80-brightgreen" alt="HTTP"/> |
| FTP | ✅ Stable | Connexion standard | <img src="https://img.shields.io/badge/FTP-21-brightgreen" alt="FTP"/> |
| SMTP | 🟡 Beta | AUTH LOGIN/PLAIN | <img src="https://img.shields.io/badge/SMTP-25-yellow" alt="SMTP"/> |
| RDP | 🟠 Alpha | Interface via rdesktop | <img src="https://img.shields.io/badge/RDP-3389-orange" alt="RDP"/> |

## 📥 Installation

```bash
# Cloner le dépôt
git clone https://github.com/servais1983/ghostcrack
cd ghostcrack

# Installer les dépendances
pip install -r requirements.txt
```

## 🚀 Exemples d'Utilisation

### SSH bruteforce

```bash
python cli.py --target 192.168.1.10 --protocol ssh --user admin --wordlist rockyou.txt --threads 10 --export results.json
```

### HTTP avec proxy SOCKS5

```bash
python cli.py --target example.com --protocol http --user admin --wordlist pass.txt --proxy socks5://127.0.0.1:9050
```

### FTP avec export PDF

```bash
python cli.py --target ftp.host --protocol ftp --user admin --wordlist pass.txt --export report.pdf
```

## 📊 Export des Résultats

- **results.json** : export JSON brut
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

## 🧠 Modules IA et Générateurs

### Prédicteur IA (ai/password_predictor.py)

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

### Générateur de Combinaisons (utils/generator.py)

```python
def generate_combinations(base, patterns=["123", "!", "2025"]):
    combos = []
    for suffix in patterns:
        combos.append(base + suffix)
        combos.append(base.capitalize() + suffix)
    return combos
```

## 🛣️ Roadmap

| Fonctionnalité | Statut |
|----------------|--------|
| Support complet RDP (rdesktop/lib) | 🟡 En cours |
| GraphQL brute-force | 🔜 À venir |
| Détection avancée (honeypots) | 🟡 En cours |
| IA renforcée (deep learning) | 🔜 À venir |
| Export HTML interactif | 🔜 À venir |
| Intégration CI/CD + API | 🟡 En cours |

## 👨‍💻 Crédits

Développé par [Servais] pour usage légal et professionnel.  
Inspiré par THC-Hydra, Medusa, et les besoins modernes en sécurité offensive.

## 📜 Licence

MIT – Utilisation libre pour usage éthique, recherche, et sécurité défensive.

---

<div align="center">
  <p>
    <a href="https://github.com/servais1983/ghostcrack/stargazers"><img src="https://img.shields.io/github/stars/servais1983/ghostcrack?style=social" alt="Stars"/></a>
    <a href="https://github.com/servais1983/ghostcrack/network/members"><img src="https://img.shields.io/github/forks/servais1983/ghostcrack?style=social" alt="Forks"/></a>
  </p>
  <p>
    <sub>🔐 Utilisez cet outil de manière responsable et uniquement dans un cadre légal 🔐</sub>
  </p>
</div>
