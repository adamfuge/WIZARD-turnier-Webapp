


export let schaetzungen = [0,2,5,2]
export let stiche = [1,2,4,1]


export function new_partie(tisch,spieler){
    let partie = {
    tisch: tisch,
    spieler: spieler,
    punktetabelle: [new Array(spieler.length).fill(0)],
    letzte_runde: 0,
    aktuelle_runde: 1,
    schaetzungen: [new Array(spieler.length).fill(0)],
    stiche: [new Array(spieler.length).fill(0)],
    geber: [,spieler[0]]
    

}
    if(partie.spieler.length==3 || partie.spieler.length==5) {partie.aktuelle_runde = 2 }
    return(partie)
}


/**Berechne die nächste Rundenzahl
*@param  {Number} partie Das aktuelle Partieobjekt
**/
export function naechste_runde(partie){
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

/**Berechne den nächsten Geber und trage ihn ein
*@param  {Number} partie Das aktuelle Partieobjekt
**/
export function naechster_geber(partie){
    
    // validierung: Spiel schon vorbei?
    if(partie.aktuelle_runde == "ende"){
        throw new Error("Spiel ist zuende")
    }
    
    //Finde den Spielerindex des letzten Geber
    let index_letzter_geber = partie.spieler.findIndex(spieler => spieler == partie.geber[partie.letzte_runde]) 
    
    let index_naechster_geber = (index_letzter_geber + 1) % partie.spieler.length

    //aktuallisiere die partie um die aktuelle rundenzahl
    partie.geber[partie.aktuelle_runde] = partie.spieler[index_naechster_geber]
} 



/** Berechne die die punktzahl der aktuellen Runde und aktuallisiere die punktetabelle
*@param  {Number} partie Das aktuelle Partieobjekt
*@param  {Array} schaetzungen Ein Array mit den abgegebenen Schätzungen
*@param  {Array} stiche Ein Array mit der tatsächlichen Stichanzahl
**/
export function update_punktetabelle(partie,schaetzungen,stiche){
    
    
    // validierung: Spiel vorbei?
    if(partie.aktuelle_runde == "ende"){
        throw new Error("Spiel ist zuende")
    }
    
    // Trage Schätzungen und Stiche in partie ein
    partie.schaetzungen[partie.aktuelle_runde] = schaetzungen
    partie.stiche[partie.aktuelle_runde] = stiche


    partie.punktetabelle[partie.aktuelle_runde] = []
    for(let i=0; i < partie.spieler.length; i++){
        if(schaetzungen[i] == stiche[i]){ 
            // Spieler hat richtig geschätzt: 20 Punkte plu 10 Punkte pro Stich
            partie.punktetabelle[partie.aktuelle_runde][i] = partie.punktetabelle[partie.letzte_runde][i] + 20 + 10*stiche[i] 
        }
        else{ 
            // Spieler hat falsch geschätzt: 10 Punkte abzug pro falsch geschätztem stich
            partie.punktetabelle[partie.aktuelle_runde][i] = partie.punktetabelle[partie.letzte_runde][i] + -10*Math.abs(stiche[i]-schaetzungen[i]) }
    }
}

/*
/**Berechne die die punktzahl der aktuellen Runde EINES Spielers
 * Unbenutzt
 *
export function berechne_partiepunkte_pro_spieler(punktesumme,schaetzung,stiche){
    "Berechne die die punktzahl der aktuellen Runde EINES Spielers"
    if(schaetzung == stiche){ punktesumme += 20 + 10*stiche }
    else{ punktesumme += -10*Math.abs(stiche-schaetzung) }
    return(punktesumme)
}
*/

/** Tue alles um die partie für die nächste runde fertig zu machen
*@param  {Number} partie Das aktuelle Partieobjekt
*@param  {Array} schaetzungen Ein Array mit den abgegebenen Schätzungen
*@param  {Array} stiche Ein Array mit der tatsächlichen Stichanzahl
**/
export function update_partie(partie,schaetzungen,stiche){
    "Tue alles um die partie für die nächste runde fertig zu machen"
    
    // validierung: Spiel vorbei?
    if(partie.aktuelle_runde == "ende"){
        throw new Error("Spiel ist zuende")
    }
    
    update_punktetabelle(partie,schaetzungen,stiche)
    naechste_runde(partie)
    naechster_geber(partie)
}

/**
*Fasse die Partie zusammen, dass in der Datenbank gespeichert werden kann
*@param {object} partie  Die gespielte Partie
*@return {Array}        Ein Array an objekten mit parametern tish, spieler, partiepunkte, turnierpunkte  
**/
export function partie_auswerten(partie){
    
    // validierung: Spiel wirklich vorbei?
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

/** Hilfsfunktion: Ermittle PLatzierungen der Einträge eines Arrays. Doppelte Plätze möglich, dann werden "fehlende" Plätze übersprungen.
 *@param  {Array} array Array an einträgen, die zu ranken sind
 *@return {Array}       Die Platzierungen (integers) in einem Array. Doppelte Einträge möglich.
 **/
export function rankings(array) {
    return array
      .map((v, i) => [v, i])
      .sort((a, b) => b[0] - a[0])
      .map(function (rank) {return (a, i, arr) => [...a, (i>0) && arr[i-1][0] === a[0] ? rank : rank = i + 1]}(0))
      .sort((a, b) => a[1] - b[1])
      .map(a => a[2]);
}

/** Hilfsfunktion: Übersetze Platzierung in Turnierpunkte
*@param  {Number} rank  Die Platzierung eines Spielers
*@return {Number}       Die resultierenden Turnierpunkte
**/
export function turnierpunkte(rank){
    const turnierpunkte_pro_platzierung = new Map([[1,45],[2,30],[3,20],[4,10],[5,5]])
    return turnierpunkte_pro_platzierung.get(rank)
}

/** Hilfsfunktion: gibt ein Array [o,1, ... , N-1] zurück
*@param  {Number} N 
*@return {Array}     [o,1, ... , N-1]
**/
export function range(N){
    let foo = [];
    for (let i = 0; i < N; i++) {
        foo.push(i);
    }
    return foo
}

/** Hilfsfunktion: gibt ein Array an doppelten Eintragen der Eingabe zurück
 *@param {Array} arr    Input
 *@return {Array}       Array an gedoppelten Einträgen des Inputs
 **/
export const findDuplicates = (arr) => {
  let sorted_arr = arr.slice().sort(); // You can define the comparing function here. 
  // JS by default uses a crappy string compare.
  // (we use slice to clone the array so the
  // original array won't be modified)
  let results = [];
  for (let i = 0; i < sorted_arr.length - 1; i++) {
    if (sorted_arr[i + 1] == sorted_arr[i]) {
      results.push(sorted_arr[i]);
    }
  }
  return results;
}

/** Gibt die Platzierungen der Spieler als Array der form [2, 3, 4, 1] zurück
*@param {object} partie  Die gespielte Partie
* @return {Array}       Die Platzierungen der Spieler zB  [2, 3, 4, 1]
**/
export function ermittle_platzierungen(partie){
    // Entferne nicht gespielte Runden aus der Punkte tabelle
    let punktetabelle_einfach = partie.punktetabelle.filter(function( element ) {return element !== undefined;})
    
    // Ermittle Platzierungen nach Partiepunkte-Endstand
    let absolute_ranks = rankings(punktetabelle_einfach[punktetabelle_einfach.length-1])
    
    // Prüfe auf Gleichplatzierungen und führe Tiebreaker1 für alle umkäpfte Plätze aus
    let umkaempfte_platzierungen = findDuplicates(absolute_ranks)
    if(umkaempfte_platzierungen.length){
        for(const platz of umkaempfte_platzierungen){
            // Indices der Spieler in der Punktetabelle für die der Tiebreaker ausgeführt werden muss
            indices = range(partie.spieler.length).filter(index => absolute_ranks[index] == platz)
            
            // Tiebreaker 1 ist: meiste richtige Schätzungen
            neue_absolute_ranks = tiebreaker1(partie,indices,platz)
            
            // Übernehme neue Platzierungen
            for(const i of indices){
                absolute_ranks[i] = neue_absolute_ranks[i]
            }
        }
    }
    
    
    return absolute_ranks
}

/**  Tiebreak nummer 1: Ermittle Platzierungen einer Spieleruntermenge entsprechend der meisten richtigen Schätzungen
* @param {object}   partie      Die gespielte Partie
* @param {Array}    indices     Die Indices, die die Untermenge an Spielern darstellt, über die der Tiebreaker angewand werden soll
* @param {Number}   umkaempfte_platzierung Die Platzierung, die der tiebreakgewinner erhalten soll
* @return {Array}       Die Platzierungen der Spieleruntermenge zB  [2, , , 3,4]
**/
export function tiebreaker1(partie,indices=range(partie.spieler.length),umkaempfte_platzierung=1){
    
    // Entferne nicht gespielte Runden aus der Punkte tabelle
    let punktetabelle_einfach = partie.punktetabelle.filter(function( element ) {return element !== undefined;})
    
    // Zähle die Anzahl richtiger Schätzungen
    let anzahl_richtiger_schaetzungen = new Array(spieler.length).fill(0)
    for(const i of indices){
        for(const runde of range(punktetabelle_einfach.length-1)){
            if(punktetabelle_einfach[runde][i]<punktetabelle_einfach[runde+1][i])anzahl_richtiger_schaetzungen[i]++
        }
    }
    
    // Ranke nach Anzahl schätzungen
    let relative_ranks = rankings(anzahl_richtiger_schaetzungen)
    let absolute_ranks = []
    for(const i of range(indices.length)){
        absolute_ranks[indices[i]] =  relative_ranks[i] - 1 + umkaempfte_platzierung
    }
    
    // Prüfe auf Gleichplatzierungen und führe Tiebraker aus
    let umkaempfte_platzierungen = findDuplicates(absolute_ranks)
    if(umkaempfte_platzierungen.length){
        for(const platz of umkaempfte_platzierungen){
            // Indices der Spieler im Tabellenblatt für die der Tiebreaker ausgeführt werden muss
            indices = range(partie.spieler.length).filter(index => absolute_ranks[index] == platz)
            
            // Tiebreaker 1 ist: meiste richtige Schätzungen
            neue_absolute_ranks = tiebreakerplatzhalter(partie,indices,platz)
            
            // Übernehme neue Platzierungen
            for(const i of indices){
                absolute_ranks[i] = neue_absolute_ranks[i]
            }
        }
    }
    
    return absolute_ranks
}

/** Platzhalter für noch nicht geschriebene Tiebreaker
* @param {object}   partie      Die gespielte Partie
* @param {Array}    indices     Die Indices, die die Untermenge an Spielern darstellt, über die der Tiebreaker angewand werden soll
* @param {Number}   umkaempfte_platzierung Die Platzierung, die der tiebreakgewinner erhalten soll
* @return {Array}       Die Platzierungen der Spieleruntermenge zB  [2, , , 3,4]
**/
export function tiebreakerplatzhalter(partie,indices=range(partie.spieler.length),umkaempfte_platzierung=1){
    
    
    let absolute_ranks = []
    for(const i of range(indices.length)){
        absolute_ranks[indices[i]] =  i + umkaempfte_platzierung
    }
    
    return absolute_ranks
}



//console.log(rankings([300,200,300]))

/* TESTS 
for(let i=1; i <= 10; i++) {
    update_partie(partie,schaetzungen,stiche)

//console.log(partie)
    
}
console.log(ermittle_platzierungen(partie))*/
