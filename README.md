# WIZARD-turnier-Webapp
Die App, die den Block der Wahrheit online Hostet, in den man die Punktzahlen einer Partie aufschreiben kann. Die Partien sollen außerdem gesammelt andgezeigt werden können.

Die Webapp verfügt über eine responsive Bootstrap-Oberfläche mit Punkteeingabe, automatischer Rundenberechnung, Undo-Funktion und vollständiger deutscher Lokalisierung.

## Projektstruktur

```
/
├── README.md                  # Diese Datei
├── Übersicht.md              # Detaillierte Projektdokumentation
└── frontend/                  # Alle Frontend-Dateien
    ├── index.html            # Startseite mit Navigation
    ├── partie_erstellen.html # Tisch- und Spielerauswahl
    ├── partie.html           # Punkteeingabe während einer Partie
    ├── partietabelle.html    # Standalone Punkteblock (für Tests)
    ├── turnierstand.html     # Gesamtwertung und Partienübersicht
    ├── style.css             # WIZARD Theme Styling
    ├── ui-handlers.js        # UI Controller und Event Handler
    ├── partieberechnungen.js # Spiellogik und Punkteberechnung
    └── partietabelle_beispiel.html # Beispiel-Partie
```

## Verwendung

1. **Starten:** Öffne `frontend/index.html` im Browser
2. **Partie erstellen:** Wähle Tisch (A-Z) und Spieler (01-99)
3. **Punkte eintragen:** Schätzungen und tatsächliche Stiche pro Runde
4. **Partie beenden:** Automatische Turnierpunkt-Berechnung
5. **Turnierstand:** Zeigt Gesamtwertung aller Spieler

## Features

- 4-Seiten Navigation (Index, Partie erstellen, Partie, Turnierstand)
- Bootstrap 5.3.3 mit responsivem Design
- Tischverwaltung (A-Z)
- Spieler-Identifikation (01-99)
- Automatische Punkteberechnung nach WIZARD-Regeln
- Undo-Funktion für letzte Runde
- Turnierpunkte-Berechnung mit Ranking
- LocalStorage-Persistenz für Partien und Turnierstand
- Vollständig auf Deutsch

## Technologie

- **Frontend:** HTML5, CSS3 (Bootstrap 5), JavaScript (ES6 Modules)
- **Datenspeicherung:** LocalStorage (Browser)
- **Icons:** Bootstrap Icons 1.11.3
- **Keine Backend-Abhängigkeiten** - läuft komplett im Browser
