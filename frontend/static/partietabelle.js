const auswaehlbare_regeln = ['Turnier','Casual']
const auswaehlbare_tische = ['A','B','C','D','E']
let partie 
const rundenzahlen_ohne_ende = [,,,[2,4,6,8,10,12,14,16,18,20],[1,3,5,7,9,11,12,13,14,15], [2,4,5,6,7,8,9,10,11,12]
        ]

function new_partie(regeln,tisch,spieler,erster_geber){
    let partie = {
    tisch: tisch,
    spieler: spieler,
    punktetabelle: [new Array(spieler.length).fill(0)],
    letzte_runde: 0,
    aktuelle_runde: 1,
    schaetzungen: [new Array(spieler.length).fill(0)],
    stiche: [new Array(spieler.length).fill(0)],
    geber: [,erster_geber],
    regeln: regeln,
    platzierungen: new Array(spieler.length).fill(1)
}
    if(partie.regeln == 'Turnier' & (partie.spieler.length==3 || partie.spieler.length==5)) {
        partie.aktuelle_runde = 2 
        partie.geber[partie.aktuelle_runde] = partie.geber[1]
    }

    return(partie)
}


/**Berechne die nächste Rundenzahl
*@param  {Number} partie Das aktuelle Partieobjekt
**/
function naechste_runde(partie){
    "Berechne die nächste Rundenzahl"
    
    // validierung: Spieleranzahl
    if(partie.regeln== 'Turnier' & (partie.spieler.length<3 ||partie.spieler.length>5)){
        throw new Error("Nicht die richtige Spieleranzahl")
    }
    // validierung: Spiel vorbei?
    if(partie.aktuelle_runde == "ende"){
        throw new Error("Spiel ist zuende")
    }
    
    //Die rundenzahlen nach Turnierordnung
    
    let rundenzahlen_nach_regeln = []

    if(partie.regeln == 'Turnier') 
        for(let i of range(60/partie.spieler.length))rundenzahlen_nach_regeln[i] = rundenzahlen_ohne_ende[partie.spieler.length][i];
    else {
        for(let i of range(60/partie.spieler.length)){
            rundenzahlen_nach_regeln[i]=i+1
        }
    }
    rundenzahlen_nach_regeln.push('ende')


    //Finde den index der aktuellen Rundenzahl
    let index = rundenzahlen_nach_regeln
    .indexOf(partie.aktuelle_runde)
    //aktuallisiere die partie um die aktuelle rundenzahl
    partie.letzte_runde = partie.aktuelle_runde
    partie.aktuelle_runde = rundenzahlen_nach_regeln[index+1]
    
} 

/**Berechne den nächsten Geber und trage ihn ein
*@param  {Number} partie Das aktuelle Partieobjekt
**/
function naechster_geber(partie){
    
    // validierung: Spiel schon vorbei?
    if(partie.letzte_runde == "ende"){
        throw new Error("Spiel ist zuende")
    }
    
    //Finde den Spielerindex des letzten Geber
    let index_letzter_geber = partie.spieler.findIndex(spieler => spieler == partie.geber[partie.letzte_runde]) 
    
    
    let index_naechster_geber = (index_letzter_geber + 1) % partie.spieler.length

    //aktuallisiere die partie um die aktuelle rundenzahl
    partie.geber[partie.aktuelle_runde] = partie.spieler[index_naechster_geber]

    let aktuellerGeber = document.getElementsByClassName('aktuellerGeber')
    for(const h of aktuellerGeber){h.innerText = `${partie.geber[partie.aktuelle_runde]}`}

} 



/** Berechne die die punktzahl der aktuellen Runde und aktuallisiere die punktetabelle
*@param  {Number} partie Das aktuelle Partieobjekt
*@param  {Array} schaetzungen Ein Array mit den abgegebenen Schätzungen
*@param  {Array} stiche Ein Array mit der tatsächlichen Stichanzahl
**/
function update_punktetabelle(partie,schaetzungen,stiche){
    
    
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
function update_partie(partie,schaetzungen,stiche){
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
function partie_auswerten(partie){
    
    // validierung: Spiel wirklich vorbei?
    if(partie.aktuelle_runde != undefined){
        throw new Error("Spiel noch nicht zuende")
    }
    
    //Per Turnierordnung festgelegt:
    let partie_ergebnisse = []
    for(let i = 0; i<partie.spieler.length; i++)
    partie_ergebnisse[i] = { 
        tisch: partie.tisch,
        spieler: partie.spieler[i],
        turnierpunkte: rankings(partie.punktetabelle[partie.letzte_runde]).map(turnierpunkte)[i],
        partiepunkte: partie.punktetabelle[partie.letzte_runde][i],
        zeitpunkt: + new Date()
}
    return partie_ergebnisse
}

/** Hilfsfunktion: Ermittle PLatzierungen der Einträge eines Arrays. Doppelte Plätze möglich, dann werden "fehlende" Plätze übersprungen.
 *@param  {Array} array Array an einträgen, die zu ranken sind
 *@return {Array}       Die Platzierungen (integers) in einem Array. Doppelte Einträge möglich.
 **/
function rankings(array) {
    return array
      .map((v, i) => [v, i])
      .sort((a, b) => b[0] - a[0])
      .map(function (rank) {return (a, i, arr) => [...a, (i>0) && arr[i-1][0] === a[0] ? rank : rank = i + 1]}(0))
      .sort((a, b) => a[1] - b[1])
      .map(a => a[2]);
}

function rankings_simple_by_lowest(array) {
    help_array = []
    for(i in array)
        help_array[i] = - array[i]

    return help_array
      .map((v, i) => [v, i])
      .sort((a, b) => b[0] - a[0])
      .map((a, i) => [...a, i + 1])
      .sort((a, b) => a[1] - b[1])
      .map(a => a[2]);
}

/** Hilfsfunktion: Übersetze Platzierung in Turnierpunkte
*@param  {Number} rank  Die Platzierung eines Spielers
*@return {Number}       Die resultierenden Turnierpunkte
**/
function turnierpunkte(rank){
    const turnierpunkte_pro_platzierung = new Map([[1,45],[2,30],[3,20],[4,10],[5,5]])
    return turnierpunkte_pro_platzierung.get(rank)
}

/** Hilfsfunktion: gibt ein Array [o,1, ... , N-1] zurück
*@param  {Number} N 
*@return {Array}     [o,1, ... , N-1]
**/
function range(N){
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
const findDuplicates = (arr) => {
  let sorted_arr = arr.slice().sort(); // You can define the comparing function here. 
  // JS by default uses a crappy string compare.
  // (we use slice to clone the array so the
  // original array won't be modified)
  let results = [];
  for (let i = 0; i < sorted_arr.length - 1; i++) {
    if (sorted_arr[i + 1] == sorted_arr[i] && sorted_arr[i] != undefined) {
      results.push(sorted_arr[i]);
    }
  }
  return new Set(results);
}



/** Gibt die Platzierungen der Spieler als Array der form [2, 3, 4, 1] zurück
*@param {object} partie  Die gespielte Partie
*@return {Array<Number>}       Die Platzierungen der Spieler zB  [2, 3, 4, 1]
**/
function ermittle_platzierungen(partie){
    console.log("ermittle Platzierungen")

    // Entferne nicht gespielte Runden aus der Punkte tabelle
    let punktetabelle_einfach = partie.punktetabelle.filter(function( element ) {return element !== undefined;})
    
    // Ermittle Platzierungen nach Partiepunkte-Endstand
    let absolute_ranks = rankings(punktetabelle_einfach[punktetabelle_einfach.length-1])
    
    // Prüfe auf Gleichplatzierungen und führe Tiebreaker1 für alle umkäpfte Plätze aus
    let umkaempfte_platzierungen = findDuplicates(absolute_ranks)

    console.log(umkaempfte_platzierungen)

    if(umkaempfte_platzierungen.size){
        for(const platz of umkaempfte_platzierungen){
            // Indices der Spieler in der Punktetabelle für die der Tiebreaker ausgeführt werden muss
            indices = range(partie.spieler.length).filter(index => absolute_ranks[index] == platz)
        

            // Tiebreaker 1 ist: meiste richtige Schätzungen
            let neue_absolute_ranks = tiebreaker1(partie,indices,platz)
            
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
function tiebreaker1(partie,indices=range(partie.spieler.length),umkaempfte_platzierung=1){
    
    console.log('Tiebreaker1')

    // Entferne nicht gespielte Runden aus der Punkte tabelle
    let punktetabelle_einfach = partie.punktetabelle.filter(function( element ) {return element !== undefined;})
    
    // Zähle die Anzahl richtiger Schätzungen
    let anzahl_richtiger_schaetzungen = new Array(partie.spieler.length).fill(0)
    for(const i of indices){
        for(const runde of range(punktetabelle_einfach.length-1)){
            if(punktetabelle_einfach[runde][i]<punktetabelle_einfach[runde+1][i])anzahl_richtiger_schaetzungen[i]++
        }
    }
    
    // Ranke nach Anzahl schätzungen
    let relative_ranks = rankings(anzahl_richtiger_schaetzungen)
    let absolute_ranks = []
    for(const i of indices){
        absolute_ranks[i] =  relative_ranks[i] - 1 + umkaempfte_platzierung
    }
    
    console.log(anzahl_richtiger_schaetzungen)
    console.log(relative_ranks)
    console.log(absolute_ranks)

    // Prüfe auf Gleichplatzierungen und führe Tiebraker aus
    let umkaempfte_platzierungen = findDuplicates(absolute_ranks)

    console.log(umkaempfte_platzierungen)

    if(umkaempfte_platzierungen.size){
        for(const platz of umkaempfte_platzierungen){
            // Indices der Spieler im Tabellenblatt für die der Tiebreaker ausgeführt werden muss
            indices = range(partie.spieler.length).filter(index => absolute_ranks[index] == platz)
            
            // Tiebreaker 1 ist: meiste richtige Schätzungen
            let neue_absolute_ranks = tiebreaker2(partie,indices,platz)
            
            // Übernehme neue Platzierungen
            for(const i of indices){
                absolute_ranks[i] = neue_absolute_ranks[i]
            }
        }
    }
    
    return absolute_ranks
}

/**  Tiebreak nummer 2: Ermittle Platzierungen einer Spieleruntermenge entsprechend dem höchsten Einzelergebnis
* @param {object}   partie      Die gespielte Partie
* @param {Array}    indices     Die Indices, die die Untermenge an Spielern darstellt, über die der Tiebreaker angewand werden soll
* @param {Number}   umkaempfte_platzierung Die Platzierung, die der tiebreakgewinner erhalten soll
* @return {Array}       Die Platzierungen der Spieleruntermenge zB  [2, , , 3,4]
**/
function tiebreaker2(partie,indices=range(partie.spieler.length),umkaempfte_platzierung=1){
    
    console.log('Tiebreaker2')
    
    // Entferne nicht gespielte Runden aus der Punkte tabelle
    let punktetabelle_einfach = partie.punktetabelle.filter(function( element ) {return element !== undefined;})
    
    // Finde das beste Einzelergebnis
    let besteEinzelergebnisse = new Array(partie.spieler.length).fill(-Infinity)
    for(const i of indices){
        for(const runde of range(punktetabelle_einfach.length-1)){
            if(punktetabelle_einfach[runde+1][i] - punktetabelle_einfach[runde][i] > besteEinzelergebnisse[i])
                besteEinzelergebnisse[i] = punktetabelle_einfach[runde+1][i] - punktetabelle_einfach[runde][i]
        }
    }
    
    // Ranke nach Anzahl schätzungen
    let relative_ranks = rankings(besteEinzelergebnisse)
    let absolute_ranks = []
    for(const i of indices){
        absolute_ranks[i] =  relative_ranks[i] - 1 + umkaempfte_platzierung
    }

    
    // console.log(besteEinzelergebnisse)
    // console.log(relative_ranks)
    // console.log(absolute_ranks)
    
    // Prüfe auf Gleichplatzierungen und führe Tiebraker aus
    let umkaempfte_platzierungen = findDuplicates(absolute_ranks)
    if(umkaempfte_platzierungen.size){
        for(const platz of umkaempfte_platzierungen){
            // Indices der Spieler im Tabellenblatt für die der Tiebreaker ausgeführt werden muss
            indices = range(partie.spieler.length).filter(index => absolute_ranks[index] == platz)
            
            // Tiebreaker 1 ist: meiste richtige Schätzungen
            let neue_absolute_ranks = tiebreaker3(partie,indices,platz,besteEinzelergebnisse)
            
            // Übernehme neue Platzierungen
            for(const i of indices){
                absolute_ranks[i] = neue_absolute_ranks[i]
            }
        }
    }
    
    return absolute_ranks
}

/**  Tiebreak nummer 3: Ermittle Platzierungen einer Spieleruntermenge entsprechend der häufigkeit des besten einzelergebnisses
* @param {object}   partie      Die gespielte Partie
* @param {Array}    indices     Die Indices, die die Untermenge an Spielern darstellt, über die der Tiebreaker angewand werden soll
* @param {Array}    besteEinzelergebnisse Die besten Einzelergebnisse der spieler, berechnet in tiebreaker1
* @param {Number}   umkaempfte_platzierung Die Platzierung, die der tiebreakgewinner erhalten soll
* @return {Array}       Die Platzierungen der Spieleruntermenge zB  [2, , , 3,4]
**/
function tiebreaker3(partie,indices=range(partie.spieler.length),umkaempfte_platzierung=1,besteEinzelergebnisse){

    console.log('Tiebreaker3')
    
    // Entferne nicht gespielte Runden aus der Punkte tabelle
    let punktetabelle_einfach = partie.punktetabelle.filter(function( element ) {return element !== undefined;})
    


    // Finde, wie oft das beste Einzelergebnis erspielt wurde
    let anzahl_besteEinzelergebnisse = new Array(partie.spieler.length).fill(0)
    for(const i of indices){
        for(const runde of range(punktetabelle_einfach.length-1)){
            if(punktetabelle_einfach[runde+1][i] - punktetabelle_einfach[runde][i] == besteEinzelergebnisse[i])
                anzahl_besteEinzelergebnisse[i]++
        }

    }
    
    
    // Ranke nach Anzahl schätzungen
    let relative_ranks = rankings(anzahl_besteEinzelergebnisse)
    let absolute_ranks = []

    
    for(const i of indices){
        absolute_ranks[i] =  relative_ranks[i] - 1 + umkaempfte_platzierung
    }

    
    // console.log(anzahl_besteEinzelergebnisse)
    // console.log(relative_ranks)
    // console.log(absolute_ranks)
    
    // Prüfe auf Gleichplatzierungen und führe Tiebraker aus
    let umkaempfte_platzierungen = findDuplicates(absolute_ranks)
    if(umkaempfte_platzierungen.size){
        for(const platz of umkaempfte_platzierungen){
            // Indices der Spieler im Tabellenblatt für die der Tiebreaker ausgeführt werden muss
            indices = range(partie.spieler.length).filter(index => absolute_ranks[index] == platz)
            
            // Tiebreaker 1 ist: meiste richtige Schätzungen
            let neue_absolute_ranks = tiebreaker4(partie,indices,platz,besteEinzelergebnisse)
            
            // Übernehme neue Platzierungen
            for(const i of indices){
                absolute_ranks[i] = neue_absolute_ranks[i]
            }
        }
    }
    
    return absolute_ranks
}

/**  Tiebreak nummer 4: Ermittle Platzierungen einer Spieleruntermenge entsprechend dem zweithöchsten Einzelergebnis
* @param {object}   partie      Die gespielte Partie
* @param {Array}    indices     Die Indices, die die Untermenge an Spielern darstellt, über die der Tiebreaker angewand werden soll
* @param {Array}    besteEinzelergebnisse Die besten Einzelergebnisse der spieler, berechnet in tiebreaker1
* @param {Number}   umkaempfte_platzierung Die Platzierung, die der tiebreakgewinner erhalten soll
* @return {Array}       Die Platzierungen der Spieleruntermenge zB  [2, , , 3,4]
**/
function tiebreaker4(partie,indices=range(partie.spieler.length),umkaempfte_platzierung=1,besteEinzelergebnisse){
    
    console.log('Tiebreaker4')

    // Entferne nicht gespielte Runden aus der Punkte tabelle
    let punktetabelle_einfach = partie.punktetabelle.filter(function( element ) {return element !== undefined;})
    
    // Finde, wie oft das beste Einzelergebnis erspielt wurde
    let zweitbesteEinzelergebnisse = new Array(partie.spieler.length).fill(0)
    for(const i of indices){
        for(const runde of range(punktetabelle_einfach.length-1)){
            if(punktetabelle_einfach[runde+1][i] - punktetabelle_einfach[runde][i] > zweitbesteEinzelergebnisse[i] && punktetabelle_einfach[runde+1][i] - punktetabelle_einfach[runde][i] < besteEinzelergebnisse[i])
                zweitbesteEinzelergebnisse[i] = punktetabelle_einfach[runde+1][i] - punktetabelle_einfach[runde][i]
        }
    }
    
    // Ranke nach Anzahl schätzungen
    let relative_ranks = rankings(zweitbesteEinzelergebnisse)
    let absolute_ranks = []
    for(const i of indices){
        absolute_ranks[i] =  relative_ranks[i] - 1 + umkaempfte_platzierung
    }

    // console.log(zweitbesteEinzelergebnisse)
    // console.log(relative_ranks)
    // console.log(absolute_ranks)
    

    // Prüfe auf Gleichplatzierungen und führe Tiebraker aus
    let umkaempfte_platzierungen = findDuplicates(absolute_ranks)
    if(umkaempfte_platzierungen.size){
        for(const platz of umkaempfte_platzierungen){
            // Indices der Spieler im Tabellenblatt für die der Tiebreaker ausgeführt werden muss
            indices = range(partie.spieler.length).filter(index => absolute_ranks[index] == platz)
            
            // Tiebreaker 1 ist: meiste richtige Schätzungen
            let neue_absolute_ranks = tiebreaker5(partie,indices,platz)
            
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
function tiebreaker5(partie,indices=range(partie.spieler.length),umkaempfte_platzierung=1){
    

    console.log('Tiebreaker5')

    
    console.log(partie.regeln)
    console.log(partie.aktuelle_runde)

    if(partie.regeln != 'Turnier' ||
        partie.aktuelle_runde != undefined){
        return new Array(partie.spieler.length).fill(umkaempfte_platzierung)
    }

   

    // FEDERICO hier muss sich ein POP up öffnen, wie
    boxContainer = document.getElementById('modalContainer')

    boxContainer.innerHTML += `
    <div id="modal${umkaempfte_platzierung}" class="modal-overlay show">
  <div class="modal-box show">
    <button id="closeBtn${umkaempfte_platzierung}" class="modal-close">×</button>
    <h3>Gleichstand</h3>
    <p>Die folgenden Spieler müssen eine Teibreaker-Runde mit 5 Karten Spielen:</p>
    <div style="padding: 10px">
    <div id="modalSpielernamen${umkaempfte_platzierung}" class="Spielernamen row"></div>
    <div id="modalschaetzunginputFelder${umkaempfte_platzierung}" class="modalschaetzunginputFelder row"></div>
    <div id="modalsticheinputFelder${umkaempfte_platzierung}" class="modalsticheinputFelder row"></div>
    </div>
    <button id="submitRundeButton${umkaempfte_platzierung}" onclick="submitTiebreaker5([${indices}],${umkaempfte_platzierung})"> Eintragen </button>
    </div>
</div>`

    tiebreaker_spieler = []
    for(const i in indices){
        tiebreaker_spieler[i] = partie.spieler[indices[i]]
    }

    reihe = document.getElementById(`modalSpielernamen${umkaempfte_platzierung}`)
    reihe.innerHTML = ''
    for(const i in tiebreaker_spieler){
        reihe.innerHTML += `
                    <span id="player${i}" class="playerName">
                      ${tiebreaker_spieler[i]}
                    </span>`
    }



    reihe = document.getElementById(`modalschaetzunginputFelder${umkaempfte_platzierung}`)
    reihe.innerHTML = ''
    for(const i in tiebreaker_spieler){
        reihe.innerHTML += `
                    <div class="col-3 inputField"> 
                      <input type="text" class="form-control schaetzunginput schaetzunginput${umkaempfte_platzierung} rundeninput inputBold" placeholder="Ansage" id="schaetzung${i}" inputmode="numeric" pattern="[0-9]*" oninput="validateNumber(this,${umkaempfte_platzierung});" style="text-align: center;"> 
                      <div class="invalid-feedback hide">
                        Invalid count
                      </div> 
                    </div>`

    }

    reihe = document.getElementById(`modalsticheinputFelder${umkaempfte_platzierung}`)
    reihe.innerHTML = ''
    for(const i in tiebreaker_spieler){
        reihe.innerHTML += `
                    <div class="col-3 inputField"> 
                      <input type="text" class="form-control stichinput stichinput${umkaempfte_platzierung} rundeninput inputBold" placeholder="Stiche" id="stiche${i}" inputmode="numeric" pattern="[0-9]*" oninput="validateNumber2(this,${umkaempfte_platzierung});" style="text-align: center;"> 
                      <div class="invalid-feedback hide">
                        Invalid count
                      </div> 
                    </div>`

    }

    modal = document.getElementById(`modal${umkaempfte_platzierung}`);
    closeBtn = document.getElementById(`closeBtn${umkaempfte_platzierung}`);

    


    /* Close when clicking outside the modal box */
    modal.addEventListener("click", function (event) {
      if (event.target === modal) {
        closeModal();
      }
    });

    /* Close when pressing Escape */
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") {
        closeModal();
      }
    });


    return new Array(partie.spieler.length).fill(umkaempfte_platzierung)
}

function closeModal(id="") {
      modal = document.getElementById(`modal${id}`);
      modal.innerHTML = ""
      modal.classList.remove("show");
      modal.classList.remove("modal-overlay");
    }


function submitTiebreaker5(indices,umkaempfte_platzierung){
        console.log("hey")
        console.log(`umkaempfte_platzierung = ${umkaempfte_platzierung}`)

        let inputs_valide = false

        if(alleFelderGefuellt(id=umkaempfte_platzierung)){
            inputs_valide = true

            if(partie.regeln=='Turnier'){
            inputs_valide = checkInputsForTurnierregeln(id=umkaempfte_platzierung)
            }
        }

        if(inputs_valide){
            // Entnehme Eingaben
            let schaetzung_inputs = document.getElementsByClassName(`schaetzunginput${umkaempfte_platzierung}`)
            let stich_inputs = document.getElementsByClassName(`stichinput${umkaempfte_platzierung}`)
            let schaetzungen = []
            let stiche = []
            let punkte = []

            console.log(indices)
            for(let i=0; i<indices.length; i++){
                console.log(i)
                stiche[i] = Number(stich_inputs[i].value)
                schaetzungen[i] = Number(schaetzung_inputs[i].value)

                if(schaetzungen[i] == stiche[i]){ 
                    // Spieler hat richtig geschätzt: 20 Punkte plu 10 Punkte pro Stich
                    punkte[i] = 20 + 10*stiche[i] 
                }
                else{ 
                    // Spieler hat falsch geschätzt: 10 Punkte abzug pro falsch geschätztem stich
                    punkte[i] = -10*Math.abs(stiche[i]-schaetzungen[i]) }
            }
            
            
            let relative_ranks = rankings(punkte)

            //console.log(partie.platzierungen)
            //console.log(indices)
            //console.log(relative_ranks)

            for(const i in indices){
                partie.platzierungen[indices[i]] =  relative_ranks[i] - 1 + umkaempfte_platzierung
            }

            console.log(partie.platzierungen)

            //Endstand updaten
            baueneu_endstandContainer()

            //Pop-up schließen
            closeModal(id=umkaempfte_platzierung)


        }
    }

/** Platzhalter für noch nicht geschriebene Tiebreaker
* @param {object}   partie      Die gespielte Partie
* @param {Array}    indices     Die Indices, die die Untermenge an Spielern darstellt, über die der Tiebreaker angewand werden soll
* @param {Number}   umkaempfte_platzierung Die Platzierung, die der tiebreakgewinner erhalten soll
* @return {Array}       Die Platzierungen der Spieleruntermenge zB  [2, , , 3,4]
**/
function tiebreakerplatzhalter(partie,indices=range(partie.spieler.length),umkaempfte_platzierung=1){
    
    
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





function bauePunktetabelle(partie){
    let punktetabelle = document.getElementById("ResultsContainer")
    let tabellencode = ``

    let rundenzahlen_nach_regeln = []

    if(partie.regeln == 'Turnier') rundenzahlen_nach_regeln = rundenzahlen_ohne_ende[partie.spieler.length];
    else {
        for(let i of range(60/partie.spieler.length)){
            rundenzahlen_nach_regeln[i]=i+1
        }
    }

    
    for(const i of rundenzahlen_nach_regeln){
        
        tabellencode += `
                    <div class="PunkteZeile"> 
                        ${baueReihe(partie,i)} 
                    </div>`
    }
    punktetabelle.innerHTML += tabellencode
}

function baueReihe(partie,i){
    if(partie.punktetabelle[i] == undefined){
        return baueLeereReihe(partie,i)
    }
    else{
        return baueVolleReihe(partie,i)
    }
}

function baueLeereReihe(partie,i){
    return `<div class="rundenzahl col-1 align-self-center p-0" style="font-weight: bold">
            ${i}
          </div>
          <div class="col-11 align-content-center p-0 pe-2">
            <div id="cardPlaceholder${i}" class="container card p-1">
              <div class="row" id="resultRow${i}">

              </div>
            </div>
          </div>
          <div style='margin-left: auto'>
            ${i==partie.aktuelle_runde ? partie.geber[i]:''}
          </div>`
}

function baueVolleReihe(partie,reihenzahl){
    let reihe = `
          <div class="rundenzahl col-1 align-self-center p-0" style="font-weight: bold">
          ${reihenzahl}
          </div>
          <div class="col-11 align-content-center p-0 pe-2">
            <div id="cardPlaceholder${reihenzahl}" class="container">
              <div class="row" id="resultRow${reihenzahl}">`
    for(const spielerindex of range(partie.spieler.length)){
        reihe += baueVolleReiheElement(partie,reihenzahl,spielerindex)
    }           
    reihe += `
              </div>
            </div>
          </div>
          <div style='width:10px'></div>
          <div style='margin-left: auto'>
            ${partie.geber[reihenzahl]}
          </div>`
    return reihe
}

function baueVolleReiheElement(partie,runde,spielerindex){
    return `
                <div class="punkteelement">
                  <div class="punktzahl">
                    ${partie.punktetabelle[runde][spielerindex]}
                  </div>
                  <div class="position-absolute top-50 start-100 translate-middle" style="padding-left: 20px">
                        <!--${partie.geber[runde]==partie.spieler[spielerindex] ? `<i class="bi-files"></i>`:``}-->
                  </div>
                  <div class="schaetzung-stiche">
                    <div class="schaetzung${partie.schaetzungen[runde][spielerindex] == partie.stiche[runde][spielerindex] ? ` bold matchColor`:``}">
                        ${partie.schaetzungen[runde][spielerindex]}
                    </div>
                    <div class="stiche${partie.schaetzungen[runde][spielerindex] == partie.stiche[runde][spielerindex] ? ` bold matchColor`:``}">
                        ${partie.stiche[runde][spielerindex]}
                    </div>
                  </div>
                </div>`
}






function neubauePunktetabelle(partie){
    let punktetabelle = document.getElementById("ResultsContainer");
    let neue_punktetabelle = document.createElement("div");
    neue_punktetabelle.id = "ResultsContainer";
    neue_punktetabelle.className = "container text-center card bg-light ps-1 pe-2 pt-2 pb-2";
    punktetabelle.replaceWith(neue_punktetabelle);
    bauePunktetabelle(partie)

}

function baue_neu_rundeninfo(partie){
    //
    let aktuelle_runde_zahl = document.getElementsByClassName('aktuelleRundenzahl')
    
    for(const h of aktuelle_runde_zahl){h.innerText = `${partie.aktuelle_runde}`}

    baue_neu_gesamtpunktzahl()

}

function validateNumber(self,id=""){

    console.log(`validating, id given is ${id}`)
    checkAndCorrectValidInput(self)

    //überprüfe ob alle Felder gefüllt sind und färbe den 'Runde eintragen Knopf'
    activateSubmitButtonIfInputsValid(id)
    
}

function validateNumber2(self,id=""){

    console.log(`validating2, id given is ${id}`)
    // Vermeide weirdes Usergefühl
    if(self.value != ''){


        if(checkAndCorrectValidInput(self) == true){
            let stichsumme = 0
            let stiche_inputs = document.getElementsByClassName(`stichinput${id}`)
            for(const i of stiche_inputs){
                if(i.value != ''){stichsumme += Number(i.value)}
            }


            if(stichsumme > partie.aktuelle_runde || (partie.aktuelle_runde == undefined && stichsumme > 5)){
                self.value = self.value.substring(0, self.value.length - 1);
            }
            else if(stichsumme == partie.aktuelle_runde || (partie.aktuelle_runde == undefined && stichsumme == 5) ){
                for(const i of stiche_inputs){
                    if(i.value == ''){i.value=0}
                }
            }
        }
    }

    activateSubmitButtonIfInputsValid(id)
}

function isPositiveInteger(string){
    return /^\d*$/.test(string)
}

function checkAndCorrectValidInput(self){
    //Versuche zuerst Eingabe zu fixen
    if(!isPositiveInteger(self.value) || 
        partie.aktuelle_runde < self.value || 
        (partie.aktuelle_runde == undefined && 5 < self.value)){

        self.value = self.value.substring(0, self.value.length - 1);
        //wenn nicht erfolgreich, lösche eingabe
        if(!isPositiveInteger(self.value) || 
            partie.aktuelle_runde < self.value ||
            (partie.aktuelle_runde == undefined && 5 < self.value)){
            self.value = ''
        }
        return false
    }
    else return true
}

function alleFelderGefuellt(id=""){
    let runden_inputs = document.getElementsByClassName(`rundeninput${id}`)
    let alle_inputs_gefüllt = true;
    for(const input of runden_inputs){
        if(input.value == ''){alle_inputs_gefüllt=false}
    }
    return alle_inputs_gefüllt
}

function reset_inputs(id=""){
    let runden_inputs = document.getElementsByClassName(`rundeninput${id}`)
    for(const input of runden_inputs){
        input.value = ''
    }
}

function disableSubmitButton(id=""){
    let submitButton = document.getElementById(`submitRundeButton${id}`)
    submitButton.classList.remove('disabled')
    submitButton.className += ' disabled'
}

function enableSubmitButton(id=""){
    let submitButton = document.getElementById(`submitRundeButton${id}`)
    submitButton.classList.remove('disabled')
}

function baue_neu_gesamtpunktzahl(){
    
    platzierungen = ermittle_platzierungen(partie)

    partie.platzierungen = platzierungen

    console.log(platzierungen)

    for(let i in partie.spieler){
        let punktzahl = document.getElementById(`punkte${i}`)
        punktzahl.innerText = partie.punktetabelle[partie.letzte_runde][i]
        
        
        if(platzierungen[i] == 1){
            punktzahl.className += ' fuehrender'

            }
        else punktzahl.classList.remove('fuehrender')
    }
}

function baue_inputcontainer(){
    baue_spielernamen()
    baue_gesamtpunktzahlen()
    baue_inputs()
}



function baue_spielernamen(){
    let reihe = document.getElementById('Spielernamen')
    reihe.innerHTML = ''
    for(const i in partie.spieler){
        reihe.innerHTML += `
                    <span id="player${i}" class="playerName">
                      ${partie.spieler[i]}
                    </span>`
    }
}

function baue_gesamtpunktzahlen(){
    let reihe = document.getElementById('gesamtpunktzahlen')
    reihe.innerHTML = ''
    for(const i in partie.spieler){
        reihe.innerHTML += `
                    <span id="punkte${i}" class="gesamtpunktzahl badge text-bg-light">
                      ${partie.punktetabelle[0][i]}
                    </span>`
    }
}

function baue_inputs(){
    let reihe = document.getElementById('schaetzunginputFelder')
    reihe.innerHTML = ''
    for(const i in partie.spieler){
        reihe.innerHTML += `
                    <div class="col-3 inputField"> 
                      <input type="text" class="form-control schaetzunginput rundeninput inputBold" placeholder="Ansage" id="schaetzung${i}" inputmode="numeric" pattern="[0-9]*" oninput="validateNumber(this);" style="text-align: center;"> 
                      <div class="invalid-feedback hide">
                        Invalid count
                      </div> 
                    </div>`

    }

    reihe = document.getElementById('sticheinputFelder')
    reihe.innerHTML = ''
    for(const i in partie.spieler){
        reihe.innerHTML += `
                    <div class="col-3 inputField"> 
                      <input type="text" class="form-control stichinput rundeninput inputBold" placeholder="Stiche" id="stiche${i}" inputmode="numeric" pattern="[0-9]*" oninput="validateNumber2(this);" style="text-align: center;"> 
                      <div class="invalid-feedback hide">
                        Invalid count
                      </div> 
                    </div>`

    }
}



function activateSubmitButtonIfInputsValid(id=""){
    let inputs_valide = false

    if(alleFelderGefuellt(id)){
        inputs_valide = true

        if(partie.regeln=='Turnier'){
        inputs_valide = checkInputsForTurnierregeln(id)
        }
    }

    if(inputs_valide){
        enableSubmitButton(id)
    }
    else disableSubmitButton(id)
}

function checkInputsForTurnierregeln(id=""){
    let inputs_valide = true

    if(!alleFelderGefuellt(id)){throw new Error('Something went wrong')}

    
    inputs_valide = inputs_valide & checkStichzahlGleichRundenzahl(id)
    
    if(partie.aktuelle_runde >= 2 || partie.aktuelle_runde == undefined){
        inputs_valide = inputs_valide & checkSchaetzungenUngleichRundenzahl(id)
    }

    return inputs_valide


}

function checkStichzahlGleichRundenzahl(id=""){
    console.log(`sgr, id given is ${id}`)
    let stichsumme = 0 
    let stiche_inputs = document.getElementsByClassName(`stichinput${id}`)
    for(const i of stiche_inputs){
        if(i.value != ''){stichsumme += Number(i.value)}
    }

    console.log(partie.aktuelle_runde)
    console.log(partie.aktuelle_runde == undefined)
    console.log(stichsumme)

    if(partie.aktuelle_runde != undefined)
        return stichsumme == partie.aktuelle_runde

    // Wenn im tiebracker spielt man mit 5 Karten
    if(partie.aktuelle_runde == undefined)
        return stichsumme == 5
}

function checkSchaetzungenUngleichRundenzahl(id=""){
    let schaetzungensumme = 0 
    let schaetzungen_inputs = document.getElementsByClassName(`schaetzunginput${id}`)
    for(const i of schaetzungen_inputs){
        if(i.value != ''){schaetzungensumme += Number(i.value)}
    }
    

    if(partie.aktuelle_runde != undefined)
        return schaetzungensumme != partie.aktuelle_runde 

    // Wenn im tiebracker spielt man mit 5 Karten
    if(partie.aktuelle_runde == undefined)
        return schaetzungensumme != 5
}


function ersetzeImputContainerMitEndstandContainer(){
    let pagerow = document.getElementById('InputContainer').parentElement
    pagerowcode = `
          <div id="EndstandContainer" class="container sticky-top text-center p-2 row fancy-bg" style="max-width: 100vw;">
            <div class="row">`

    bla = rankings_simple_by_lowest(partie.platzierungen)
    anzeigereihenfolge = []
    for(let i=1; i<=bla.length; i++){
        anzeigereihenfolge[i-1] = bla.indexOf(i)
    }

    pagerowcode +=`
            <div id='platzierungenspalte' class='endstandspalte'>`
    pagerowcode += EndstandSpaltePlatzierungen(anzeigereihenfolge)
    pagerowcode +=`
            </div>
            <div id='spielerspalte' class='endstandspalte'>`
    pagerowcode += EndstandSpalteSpieler(anzeigereihenfolge)
    pagerowcode +=`
            </div>
            <div id='ppspalte' class='endstandspalte'>`
    pagerowcode += EndstandSpaltePartiepunkte(anzeigereihenfolge)
    pagerowcode +=`
            </div>`
    if(partie.regeln=='Turnier') {
        pagerowcode +=`
                <div id='tpspalte' class='endstandspalte'>`
        pagerowcode += EndstandSpalteTurnierpunkte(anzeigereihenfolge)
        pagerowcode += `
        </div>`
        }
    
    pagerowcode += `
    </div>`

    
    if(partie.regeln=='Turnier') {
        pagerowcode += EndstandSpielAbschliessenButton()
        
    }
    else {
        pagerowcode += EndstandNeuePartieButton()
    }
    
    pagerowcode += `
    </div>`

    pagerow.innerHTML = pagerowcode
    

    if(partie.regeln=='Turnier') {
        SpielAbschliessen = document.getElementById('SpielAbschliessen')
        SpielAbschliessen.onclick = function(){
            if(partie.aktuelle_runde != undefined){throw new Error('Partie scheint noch nicht vorbei zu sein')}

            let spielergebnisse = partie_auswerten(partie)

            //POST the spielergebnisse to the backend
            fetch('/post_match_result', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(spielergebnisse),
            })
            .then(response => response.text())
            .then(data => {
                console.log('Success:', data);
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        
        }
    }
    else {
        let neuepartiebuttons = document.getElementsByClassName('neuepartiebutton')
        for(const neuepartiebutton of neuepartiebuttons){
            neuepartiebutton.onclick = LadeNeuePartieErstellen
        }
        
        
    }

    leereNavContainer()

    
}
    
function baueneu_endstandContainer(){
    bla = rankings_simple_by_lowest(partie.platzierungen)
    anzeigereihenfolge = []
    for(let i=1; i<=bla.length; i++){
        anzeigereihenfolge[i-1] = bla.indexOf(i)
    }

    console.log(anzeigereihenfolge)

    spalte = document.getElementById("platzierungenspalte")

    spalte.innerHTML = EndstandSpaltePlatzierungen(anzeigereihenfolge)

    spalte = document.getElementById("spielerspalte")

    spalte.innerHTML = EndstandSpalteSpieler(anzeigereihenfolge)

    spalte = document.getElementById("ppspalte")

    spalte.innerHTML = EndstandSpaltePartiepunkte(anzeigereihenfolge)

    if(partie.regeln=='Turnier') {

    spalte = document.getElementById("tpspalte")

    spalte.innerHTML = EndstandSpalteTurnierpunkte(anzeigereihenfolge)

    }
}


function EndstandSpaltePlatzierungen(anzeigereihenfolge){
    code = `
              <div class='endstandspaltenheader'>
                Platz
              </div>`
    for(i of anzeigereihenfolge)
        code += `
              <div id='platzendstandreihe${i}' class="endstandspaltenelement platz${partie.platzierungen[i]}">
                ${partie.platzierungen[i]}
              </div>`
    

    return code
}

function EndstandSpalteSpieler(anzeigereihenfolge){
    code = `
              <div class='endstandspaltenheader'>
                Spieler
              </div>`
    for(i of anzeigereihenfolge){
        code += `
              <div id='spielerendstandreihe${i}' class="endstandspaltenelement">
                ${partie.spieler[i]}
              </div>`
        }
    return code
}

function EndstandSpaltePartiepunkte(anzeigereihenfolge){
    code = `
              <div class='endstandspaltenheader'>
                EP
              </div>`
    for(i of anzeigereihenfolge){
        code += `
              <div id='ppendstandreihe${i+1}' class="endstandspaltenelement">
                ${partie.punktetabelle[partie.letzte_runde][i]}
              </div>`
        }

    return code
}

function EndstandSpalteTurnierpunkte(anzeigereihenfolge){
    code = `
              <div class='endstandspaltenheader'>
                TP
              </div>`
    for(i of anzeigereihenfolge){
        code += `
              <div id='tpendstandreihe${i+1}' class="endstandspaltenelement">
                ${turnierpunkte(partie.platzierungen[i])}
              </div>`
        }

    return code
}

function EndstandNeuePartieButton(){
    return `
    <button type="button" class="neuepartiebutton" onclick="load('s1')">
                      <i class="bi-stars pe-1">
                      </i>Neue Partie</button>`
}

function EndstandSpielAbschliessenButton(){
    return `
           <button type="button" id="SpielAbschliessen" > Partie beenden und absenden </button>`
}

function baueInputUndResultsContainer(){
    let block = document.getElementById('blockContainer')
    block.innerHTML = `
    <div class="col-xs-12 col-sm-12 col-md-12 col-lg-1 space" id="spaceStart">
			</div>
      
      <div class="pagerow">
			  <div class="col-xs-12 col-sm-12 col-md-12 col-lg-10" id="block">
          <div id="InputContainer" class="container sticky-top text-center p-2 " style="max-width: 100vw;">
            <div class="row">
              <div class="col-1 align-self-center p-0">
                <div id="rundeninfo">
                  Runde
                  <span class="aktuelleRundenzahl">
                    1
                  </span>
                </div>
              </div>
              <div class="container">
                <div id="Spielernamen" class="Spielernamen" data-bs-toggle="tooltip" data-bs-placement="right" data-bs-title="Name">
                </div>
                <div id="gesamtpunktzahlen" data-bs-toggle="tooltip" data-bs-placement="right" data-bs-title="Total score">
                </div>
                <div class="inputtitel"> 
                  Angesagte Stiche
                </div>
                <div id='schaetzunginputFelder' class="row" data-bs-toggle="tooltip" data-bs-placement="right" data-bs-title="Bid">
                </div> 
                <div class="inputtitel"> 
                  Tatsächliche Stiche
                </div>
                <div id='sticheinputFelder' class="row" data-bs-toggle="tooltip" data-bs-placement="right" data-bs-title="Actual">
                </div>
              <div id="InputSubmit" class=""> 
                <button type="button" id="submitRundeButton" class="btn btn-primary disabled" >
                  <i class="bi-box-arrow-in-down pe-1"></i>
                  Runde  
                  <span class="aktuelleRundenzahl">
                    1
                  </span>
                  eintragen
                </button> 
              </div>
            </div>
          </div>
        </div>
      </div>
      </div>
      <!--<div class="modal fade" id="modalUndoRound" tabindex="-1" aria-labelledby="modalUndoRoundLabel" aria-hidden="true"> 
        <div class="modal-dialog"> 
          <div class="modal-content"> 
            <div class="modal-header"> 
              <h1 class="modal-title fs-5" id="modalUndoRoundLabel">
                Undo last round?
              </h1> 
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close">

              </button> 
            </div> 
            <div id="modalUndoRoundBody" class="modal-body">
              Do you really want to undo last round? 
            </div> 
            <div class="modal-footer"> 
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                No
              </button> 
              <button type="button" class="btn btn-danger" data-bs-dismiss="modal" onclick="undoRound()">
                Yes, undo
              </button> 
            </div> 
          </div> 
        </div> 
      </div>-->
      <div class="pagerow"> 
        <div id="ResultsContainer" class="container text-center card bg-light ps-1 pe-2 pt-2 pb-2">
        </div>
      </div>`

    // Definiere erst onclickfunktion, wenn button existier. sonst fehler
    let submitButton = document.getElementById('submitRundeButton')
    submitButton.onclick = function(){
        

        let inputs_valide = false

        if(alleFelderGefuellt()){
            inputs_valide = true

            if(partie.regeln=='Turnier'){
            inputs_valide = checkInputsForTurnierregeln()
            }
        }

        if(inputs_valide){
            // Entnehme Eingaben
            let schaetzung_inputs = document.getElementsByClassName('schaetzunginput')
            let stich_inputs = document.getElementsByClassName('stichinput')
            let schaetzungen = []
            let stiche = []
            for(let i in partie.spieler){
                stiche[i] = Number(stich_inputs[i].value)
                schaetzungen[i] = Number(schaetzung_inputs[i].value)
            }


            // Prüfe eingaben
            
            // Update Partie
            update_partie(partie,schaetzungen,stiche)


            // Baue die Punktetabelle neu
            neubauePunktetabelle(partie)
            
            // Baue die Rundeninfos neu
            baue_neu_rundeninfo(partie)
            

            // Setze Inputs und Submitbutton zurück
            reset_inputs()
            disableSubmitButton()

            console.log(partie.aktuelle_runde) 


            if(partie.aktuelle_runde == undefined){
                ersetzeImputContainerMitEndstandContainer()

            }

            
        }
    }
}

function bauePartieerstellenContainer(){
    block = document.getElementById('blockContainer')

    block.innerHTML = `
    <div class="pagerow">
      <div id="PartieerstellenContainer">
        <h2 class="partieerstellenelement">Partie Erstellen</h2>
        <label class="partieerstellenelement"> Regeln:
        <select id="RegelnWaehlen" >
          <option value='Turnier' selected>Turnier</option>
          <option value='Casual'>Casual</option>
        </select>
        </label>
        <label class="partieerstellenelement">
        Tisch:
        <select id="TischWaehlen" >
          <option value='' selected disabled></option>
        </select>
        </label>
        <div class="partieerstellenelement">
          <h5>Spieler</h5>
          <div id="SpielernamenInputs">
            <input id="spielernameninput0" class="spielernameninput" style="text-align: center;">
            <input id="spielernameninput1" class="spielernameninput" style="text-align: center;">
            <input id="spielernameninput2" class="spielernameninput" style="text-align: center;">
            <input id="spielernameninput3" class="spielernameninput" placeholder="optional" style="text-align: center;">
            <input id="spielernameninput4" class="spielernameninput" placeholder="optional" style="text-align: center;">
          </div>
        </div>
        <label class="partieerstellenelement"> Erster Geber:
        <select id="GeberWaehlen" >
        </select>
        </label>
        <button id='PartieErstellenButton'class="partieerstellenelement"> Partie beginnen</button>

        </div>


      </div>`
    
    baueTischAuswahl()

    let spielernameninputs=document.getElementsByClassName('spielernameninput')
    for(const inputbox of spielernameninputs){
        let RegelnWaehlen = document.getElementById('RegelnWaehlen')
        inputbox.oninput = function(){
            if(inputbox.value != ''){
                if(RegelnWaehlen.value=='Turnier'){
                    if(!isPositiveInteger(inputbox.value) | 0 == inputbox.value){
                        inputbox.value = inputbox.value.substring(0, inputbox.value.length - 1);
                        //wenn nicht erfolgreich, lösche eingabe
                        if(!isPositiveInteger(inputbox.value) | 0 == inputbox.value){
                            inputbox.value = ''
                        }
                    }
                else
                inputbox.value = Number(inputbox.value)
                }
            }

            baueGeberAuswahl()

        }
    }


    let RegelnWaehlen=document.getElementById('RegelnWaehlen')
    RegelnWaehlen.onchange = function(){
        let spielernameninput=document.getElementsByClassName('spielernameninput')
        for(const inputbox of spielernameninput){
            inputbox.oninput()
        }
        
        if(RegelnWaehlen.value == 'Turnier'){
            let spielernameninput5 = document.getElementById('spielernameninput5')
            if(spielernameninput5 != undefined) spielernameninput5.remove()
        }
        else if(RegelnWaehlen.value == 'Casual'){
            let SpielernamenInputs=document.getElementById('SpielernamenInputs')
            SpielernamenInputs.innerHTML += `
            <input id="spielernameninput5" class="spielernameninput" placeholder="optional" style="text-align: center;">`
            
            
            let spielernameninputs=document.getElementsByClassName('spielernameninput')
            for(const inputbox of spielernameninputs){
                let RegelnWaehlen = document.getElementById('RegelnWaehlen')
                inputbox.oninput = function(){
                    if(inputbox.value != ''){
                        if(RegelnWaehlen.value=='Turnier'){
                            if(!isPositiveInteger(inputbox.value) | 0 == inputbox.value){
                                inputbox.value = inputbox.value.substring(0, inputbox.value.length - 1);
                                //wenn nicht erfolgreich, lösche eingabe
                                if(!isPositiveInteger(inputbox.value) | 0 == inputbox.value){
                                    inputbox.value = ''
                                }
                            }
                        else
                        inputbox.value = Number(inputbox.value)
                        }
                    }
                    baueGeberAuswahl()
                }
            }
        

        }

        baueGeberAuswahl()
    }

    let PartieErstellenButton = document.getElementById('PartieErstellenButton')
    PartieErstellenButton.onclick = function(){
        let RegelnWaehlen = document.getElementById('RegelnWaehlen')
        let TischWaehlen = document.getElementById('TischWaehlen')
        let SpielernamenInputs=document.getElementsByClassName('spielernameninput')
        let GeberWaehlen = document.getElementById('GeberWaehlen')
        if(RegelnWaehlen.value != '' &
            TischWaehlen.value != '' &
            SpielernamenInputs[0].value != '' &
            SpielernamenInputs[1].value != '' &
            SpielernamenInputs[2].value != '' &
            GeberWaehlen.value != ''){
            
            let spieler = []
            for(const spielernamen of SpielernamenInputs){
                if(spielernamen.value != ''){
                    spieler.push(spielernamen.value)
                }
            }


            if(findDuplicates(spieler).size == 0){
                    
                // Yay, Partie kann beginnen
                partie = new_partie(RegelnWaehlen.value,
                                    TischWaehlen.value,
                                    spieler,
                                    GeberWaehlen.value)
                

                baueInputUndResultsContainer()

                bauePunktetabelle(partie)


                baue_inputcontainer()

                baue_neu_rundeninfo(partie)

                baueNavContainer()
                
                }
            }
    }
}

function baueTischAuswahl(){
    let TischWaehlen = document.getElementById('TischWaehlen')
    for(const tisch of auswaehlbare_tische){
        TischWaehlen.innerHTML += `
        <option> ${tisch} </option>`
    }
}

function baueGeberAuswahl(){
    let GeberWaehlen = document.getElementById('GeberWaehlen')
    GeberWaehlen.innerHTML = ''
    for(const inputbox of document.getElementsByClassName('spielernameninput')){
        if(inputbox.value != '') GeberWaehlen.innerHTML += `
        <option value='${inputbox.value}'> ${inputbox.value} </option>`
    }
}

function baueNavContainer(){
    let cont = document.getElementById('aktuelleRundeninfo')
    cont.innerHTML = `
                  <div class="d-flex" style="display: flex; flex-direction: column; align-items:center; "> 
                    	<span id="roundInfo" style="font-size:1.3rem;font-weight:bold;">
                          <span class="">
                            ${partie.regeln}
                          </span>,
                          Tisch
                          <span class="">
                            ${partie.tisch}
                          </span>,
                          Runde 
                          <span class="aktuelleRundenzahl">
                            ${partie.aktuelle_runde}
                          </span>
                      </span>
                    <div>
                      <span id="roundInfo2">
                        Spieler
                        <span class="aktuellerGeber">
                            ${partie.geber[partie.aktuelle_runde]}
                        </span> 
                        gibt jedem
                        <span class="aktuelleRundenzahl">
                            ${partie.aktuelle_runde}
                        </span> 
                        Karten
                      </span>
                    </div> 
                  </div> `
}

function leereNavContainer(){
    let cont = document.getElementById('aktuelleRundeninfo')
    cont.innerHTML = ``
}

function leereblockContainer(){
    let cont = document.getElementById('blockContainer')
    cont.innerHTML = ``

}

function LadeNeuePartieErstellen(){
    leereNavContainer()
    leereblockContainer()
    bauePartieerstellenContainer()
}

let neuepartiebuttons = document.getElementsByClassName('neuepartiebutton')
for(const neuepartiebutton of neuepartiebuttons){
    neuepartiebutton.onclick = LadeNeuePartieErstellen
}



function TestLadeEndstand(){
    let schaetzungen = [0,2,5,2,4]
    let stiche = [1,2,4,1,4]
    
    partie = new_partie(regeln='Turnier','A',['Adam ','Bdam','Cdam'],'Adam')
    
    update_partie(partie,schaetzungen,stiche)
    update_partie(partie,schaetzungen,stiche)
    update_partie(partie,schaetzungen,stiche)
    update_partie(partie,schaetzungen,stiche)
    update_partie(partie,schaetzungen,stiche)
    update_partie(partie,schaetzungen,stiche)
    update_partie(partie,schaetzungen,stiche)
    update_partie(partie,schaetzungen,stiche)
    update_partie(partie,schaetzungen,stiche)

    baueInputUndResultsContainer()

    bauePunktetabelle(partie)


    baue_inputcontainer()

    baue_neu_rundeninfo(partie)
    baueNavContainer()

}



function testEndstandTiebreaker1(){
    let schaetzungen = [0,5,5,0,0]
    let stiche = [0,5,5,0,0]
    
    partie = new_partie(regeln='Turnier','A',['Adam ','Bdam','Cdam','Ddam','Edam'],'Adam')
    
    update_partie(partie,schaetzungen,stiche)
    update_partie(partie,[0,5,4,5,4],[5,4,4,4,4])
    update_partie(partie,[0,5,4,5,4],[5,5,4,5,4])
    update_partie(partie,[0,5,4,5,4],[5,5,4,5,4])
    update_partie(partie,[0,5,4,5,4],[5,5,4,5,4])
    update_partie(partie,[0,5,4,5,4],[5,5,4,5,4])
    update_partie(partie,[0,5,4,5,4],[5,5,4,5,4])
    update_partie(partie,[0,5,4,5,4],[5,5,4,5,4])
    update_partie(partie,[0,5,4,5,4],[5,5,4,5,4])

    baueInputUndResultsContainer()

    bauePunktetabelle(partie)


    baue_inputcontainer()

    baue_neu_rundeninfo(partie)
    baueNavContainer()
}

function testEndstandTiebreaker2(){
    let schaetzungen = [0,5,5]
    let stiche = [5,5,5]
    
    partie = new_partie(regeln='Turnier','A',['Adam ','Bdam','Cdam'],'Adam')
    
    update_partie(partie,schaetzungen,stiche)
    update_partie(partie,schaetzungen,stiche)
    update_partie(partie,schaetzungen,stiche)
    update_partie(partie,schaetzungen,stiche)
    update_partie(partie,schaetzungen,stiche)
    update_partie(partie,schaetzungen,stiche)
    update_partie(partie,schaetzungen,stiche)
    update_partie(partie,[0,5,4],[5,5,4])
    update_partie(partie,[0,5,6],[5,5,6])

    baueInputUndResultsContainer()

    bauePunktetabelle(partie)


    baue_inputcontainer()

    baue_neu_rundeninfo(partie)
    baueNavContainer()
}



function testEndstandTiebreaker3(){
    let schaetzungen = [0,5,5]
    let stiche = [5,5,5]
    
    partie = new_partie(regeln='Turnier','A',['Adam ','Bdam','Cdam'],'Adam')
    
    update_partie(partie,schaetzungen,stiche)
    update_partie(partie,schaetzungen,stiche)
    update_partie(partie,schaetzungen,stiche)
    update_partie(partie,schaetzungen,stiche)
    update_partie(partie,schaetzungen,stiche)
    update_partie(partie,schaetzungen,stiche)
    update_partie(partie,schaetzungen,stiche)
    update_partie(partie,[5,5,4],[5,5,4])
    update_partie(partie,[0,3,4],[5,3,4])

    baueInputUndResultsContainer()

    bauePunktetabelle(partie)


    baue_inputcontainer()

    baue_neu_rundeninfo(partie)
    baueNavContainer()
}

function testEndstandTiebreaker4(){
    let schaetzungen = [0,5,5]
    let stiche = [5,5,5]
    
    partie = new_partie(regeln='Turnier','A',['Adam ','Bdam','Cdam'],'Adam')
    
    update_partie(partie,schaetzungen,stiche)
    update_partie(partie,schaetzungen,stiche)
    update_partie(partie,schaetzungen,stiche)
    update_partie(partie,schaetzungen,stiche)
    update_partie(partie,schaetzungen,stiche)
    update_partie(partie,schaetzungen,stiche)
    update_partie(partie,[0,5,5],[5,5,5])
    update_partie(partie,[0,2,1],[5,2,1])
    update_partie(partie,[0,3,4],[5,3,4])

    baueInputUndResultsContainer()

    bauePunktetabelle(partie)


    baue_inputcontainer()

    baue_neu_rundeninfo(partie)
    baueNavContainer()
}

function testEndstandTiebreaker5(){
    let schaetzungen = [0,5,5,0,0]
    let stiche = [5,5,5,5,5]
    
    partie = new_partie(regeln='Turnier','A',['Adam ','Bdam','Cdam','Ddam','Edam'],'Adam')
    
    update_partie(partie,schaetzungen,stiche)
    update_partie(partie,schaetzungen,stiche)
    update_partie(partie,schaetzungen,stiche)
    update_partie(partie,schaetzungen,stiche)
    update_partie(partie,schaetzungen,stiche)
    update_partie(partie,schaetzungen,stiche)
    update_partie(partie,schaetzungen,stiche)
    update_partie(partie,schaetzungen,stiche)
    update_partie(partie,schaetzungen,stiche)

    baueInputUndResultsContainer()

    bauePunktetabelle(partie)


    baue_inputcontainer()

    baue_neu_rundeninfo(partie)
    baueNavContainer()
}

// TestLadeEndstand()
testEndstandTiebreaker5()







////////////////// Führe aus

/*


const rundenzahlen_ohne_ende = [,,,[2,4,5,6,7,8,9,10,11,12],[1,3,5,7,9,11,12,13,14,15], [2,4,6,8,10,12,14,16,18,20]
        ]


*/

