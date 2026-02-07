let partie = new_partie(tisch= "A",
    spieler= [1,2,3])

let schaetzungen = [0,2,5,2]
let stiche = [0,2,4,1]


function new_partie(tisch,spieler){
    let partie = {
    tisch: "A",
    spieler: spieler,
    punktetabelle: [new Array(spieler.length).fill(0)],
    letzte_runde: 0,
    aktuelle_runde: 1,
    anzahl_richtiger_schätzungen: new Array(spieler.length).fill(0)
    }
    if(partie.spieler.length==3 || partie.spieler.length==5) {partie.aktuelle_runde = 2 }
    return(partie)
}

function naechste_runde(partie){
    "Berechne die nächste Rundenzahl"
    
    // validierung: Spieleranzahl
    if(partie.spieler.length<3 ||partie.spieler.length>5){
        throw new Error("Nicht die richtige Spieleranzahl")
    }
    // validierung: Spiel vorbei?
    if(partie.aktuelle_runde == "ende"){
        throw new Error("Spiel ist zuende")
    }
    
    //Die rundenzahlen nach Turnierordnung
    const rundenzahlen = [,,,[2,4,5,6,7,8,9,10,11,12,'ende'],[1,3,5,7,9,11,12,13,14,15,'ende'], [2,4,6,8,10,12,14,16,18,20,'ende']
        ]
    //Finde den index der aktuellen Rundenzahl
    let index = rundenzahlen[partie.spieler.length].indexOf(partie.aktuelle_runde)
    //aktuallisiere die partie um die aktuelle rundenzahl
    partie.letzte_runde = partie.aktuelle_runde
    partie.aktuelle_runde = rundenzahlen[partie.spieler.length][index+1]
    
} 






function update_punktetabelle(partie,schaetzungen,stiche){
    "Berechne die die punktzahl der aktuellen Runde und aktuallisiere die punktetabelle"
    
    // validierung: Spiel vorbei?
    if(partie.aktuelle_runde == "ende"){
        throw new Error("Spiel ist zuende")
    }
    
    partie.punktetabelle[partie.aktuelle_runde] = []
    
    for(let i=0; i < partie.spieler.length; i++){
        if(schaetzungen[i] == stiche[i]){ 
            // Spieler hat richtig geschätzt: 20 Punkte plu 10 Punkte pro Stich
            partie.punktetabelle[partie.aktuelle_runde][i] = partie.punktetabelle[partie.letzte_runde][i] + 20 + 10*stiche[i] 
            // richtige schätzungen mitzählen, für Tiebreaker 
            partie.anzahl_richtiger_schätzungen[i] += 1
        }
        else{ 
            // Spieler hat falsch geschätzt: 10 Punkte abzug pro falsch geschätztem stich
            partie.punktetabelle[partie.aktuelle_runde][i] = partie.punktetabelle[partie.letzte_runde][i] + -10*Math.abs(stiche[i]-schaetzungen[i]) }
    }
}

function berechne_partiepunkte_pro_spieler(punktesumme,schaetzung,stiche){
    "Berechne die die punktzahl der aktuellen Runde EINES Spielers"
    if(schaetzung == stiche){ punktesumme += 20 + 10*stiche }
    else{ punktesumme += -10*Math.abs(stiche-schaetzung) }
    return(punktesumme)
}

function update_partie(partie,schaetzungen,stiche){
    "Tue alles um die partie für die nächste runde fertig zu machen"
    
    // validierung: Spiel vorbei?
    if(partie.aktuelle_runde == "ende"){
        throw new Error("Spiel ist zuende")
    }
    
    update_punktetabelle(partie,schaetzungen,stiche)
    naechste_runde(partie)
}

function partie_auswerten(partie){
    "Fasse die Partie zusammen, dass sie als JSON in der Datenbank gespeichert werden kann"
    
    // validierung: Spiel vorbei?
    if(partie.aktuelle_runde != "ende"){
        throw new Error("Spiel noch nicht zuende")
    }
    
    //Per Turnierordnung festgelegt:
    let partie_ergebnisse = []
    for(let i = 0; i<partie.spieler.length; i++)
    partie_ergebnisse[i] = { 
        tisch: partie.tisch,
        spieler: partie.spieler[i],
        turnierpunkte: rankings(partie.punktetabelle[partie.letzte_runde]).map(turnierpunkte)[i],
        partiepunkte: partie.punktetabelle[partie.letzte_runde][i]
}
    return partie_ergebnisse
}

function rankings(array) {
    return array
      .map((v, i) => [v, i])
      .sort((a, b) => b[0] - a[0])
      .map(function (rank) {return (a, i, arr) => [...a, (i>0) && arr[i-1][0] === a[0] ? rank : rank = i + 1]}(0))
      .sort((a, b) => a[1] - b[1])
      .map(a => a[2]);
}

function turnierpunkte(rank){
    const turnierpunkte_pro_platzierung = new Map([[1,45],[2,30],[3,20],[4,10],[5,5]])
    return turnierpunkte_pro_platzierung.get(rank)
}



//console.log(rankings([300,200,300]))

/* TESTS*/ 
for(let i=1; i <= 10; i++) {
    update_partie(partie,schaetzungen,stiche)

console.log(partie)
    
}
console.log(partie_auswerten(partie))
