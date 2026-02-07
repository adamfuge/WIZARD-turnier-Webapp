# Projektübersicht



## Frontend
4 Seiten werden für volle funktionalität benötigt. Diese sollen in htnl geschrieben sein. CSS und Flexbox erweisen sich fürs Design möglicherweise als nützlich.

### index.html
Die Eingangsseite. Bietet die option auf Partie_erstellen.html oder turnierstand.html

### partie_erstellen.html
Auf dieser Seite wird der aktuelle Stand einer Partie eingetragen werden können.

#### Auswahl eines Tisches
Beim Turnier wird es die Tische A-Z geben, diesen sollte man im header auswählen können

#### Eintragen der Spieler
Die Spieler werden im Turnier mit Zahlen 01 - 99 identifiziert. Wer teil der Runde ist, sollte man eintragen können


### partie.html
Hier werden die Punkte einer Partie eingetragen
(man könnte auch 26 Seiten partieA.html bis partieZ.html verwenden, da an jedem Tisch maximal eine Partie gleichzeitig stattfindet)


### turnierstand.html
Hier sollen die Partien aufgelistet sein.
Eventuell könnte hier auch die Berechnung der Aktuellen Turnierpunktzahl der Spieler stehen.


## Backend
### Partieerstellung
Eine Partie ist zunächst zu speichern als JSON mit den parametern
- tisch, ein Character wie "A"
- spieler, ein Array mit Zahlen 01 bis 99, diese identifizieren die Spieler
- punktetabelle, ein ?Table? initialisiert als [[0,0,0,0]] d.h. (Adam stellt sich das vor, wie) ein Array gefüllt mit Arrays, die eine Zeile des Block der Wahrheit darstellt + der 0. eintrag sind 0en. Beispiel:
  [[0,0,0,0],[20,-10,20,30],,[40,-20,0,50],,,[60,-40,50,30]]
- aktuelle_runde, eine Zahl initialisiert als 1, stellt die erste leere zeile im Block der Wahrheit dar

### Berechnung der Partiepunkte
Erhalte: 
- schaetzungen, ein Array mit Zahlen 0-20, die Schätzungen der Stichanzahl
- stiche, ein Array mit Zahlen 0-20, die tatsächliche anzahl an stichen
- die gespeicherte partie

die punktzahl einer runde berechnet sich
- Fall: richtig geschätzt, 20 + 10*schaetzungen
- Fall: falsch geschätzt, -10*abs(schaetzungen-stiche)
berechne nun punktetabelle[aktuelle_runde] = punktetabelle[punktetabelle.length()] + punktzahl

Gebe zurück:
- die gespeicherte partie, bei der
  - punktetabelle um eine Zeile erweitert wurde
  - aktuelle_runde um '1' erhöht*

*Bei turnieren werden nur ausgewählte Runden gespielt:
- 3 Spieler: [2,4,5,6,7,8,9,10,11,12]
- 4 Spieler: [1,3,5,7,9,11,12,13,14,15]
- 5 Spieler: [2,4,6,8,10,12,14,16,18,20]

### berechnung der nächsten rundenanzahl
ToDo

### Partiespeicherung
Eine fertige Partie wird als JSON gespeichert mit Parametern:
- tisch, ein Character wie "A"
- spieler, ein Array mit Zahlen 01 bis 99, diese identifizieren die Spieler
- partiepunkte, ein Array mit Zahlen, die endpunkzahl der spieler der partie
- anzahl_richtiger_schätzungen, ein Array mit Zahlen, die Anzahlen, wie oft spieler richtig geschätzt haben.

### Turnierstand
Ein ?JSON?, eine ?Tabelle? mit den Spalten
- spieler, Zahlen 01 bis 99, diese identifizieren die Spieler
- summe_turnierpunkte, Zahlen in Zehnerschritten, die Summe der bisher erhaltenen Turnierpunkte der spieler der partie
- summe_partiepunkte, Zahlen in Zehnerschritten, die Summe endpunkzahl der spieler der partie


#### Initialisieren:
erhalte:
- spielerzahl

erschaffe:
- spieler = 01 bis spielerzahl
- summe_turnierpunkte= 0
- summe_partiepunkte= 0
  
### Updaten des Turnierstands
Bei neuer abgeschlossenen partie:
- ermittle ranking der spieler nach partiepunkten, bei unentschieden entscheidet die anzahl richtiger schätzungen
- Weise Turnierpunkte zu: Letzer platz = 10 Punkte, Vorletzer = 20, ...


