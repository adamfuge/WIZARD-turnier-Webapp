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
    regeln: regeln
    

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
    if (sorted_arr[i + 1] == sorted_arr[i]) {
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
function tiebreaker1(partie,indices=range(partie.spieler.length),umkaempfte_platzierung=1){
    
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
            let neue_absolute_ranks = tiebreakerplatzhalter(partie,indices,platz)
            
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

function validateNumber(self){

    checkAndCorrectValidInput(self)
    //überprüfe ob alle Felder gefüllt sind und färbe den 'Runde eintragen Knopf'

    activateSubmitButtonIfInputsValid()
    
}

function validateNumber2(self){

    // Vermeide weirdes Usergefühl
    if(self.value != ''){


        if(checkAndCorrectValidInput(self) == true){
            let stichsumme = 0
            let stiche_inputs = document.getElementsByClassName('stichinput')
            for(const i of stiche_inputs){
                if(i.value != ''){stichsumme += Number(i.value)}
            }


            if(stichsumme > partie.aktuelle_runde){
                self.value = self.value.substring(0, self.value.length - 1);
            }
            else if(stichsumme == partie.aktuelle_runde){
                for(const i of stiche_inputs){
                    if(i.value == ''){i.value=0}
                }
            }
        }
    }

    activateSubmitButtonIfInputsValid()
}

function isPositiveInteger(string){
    return /^\d*$/.test(string)
}

function checkAndCorrectValidInput(self){
    //Versuche zuerst Eingabe zu fixen
    if(!isPositiveInteger(self.value) | partie.aktuelle_runde < self.value){
        self.value = self.value.substring(0, self.value.length - 1);
        //wenn nicht erfolgreich, lösche eingabe
        if(!isPositiveInteger(self.value) | partie.aktuelle_runde < self.value){
            self.value = ''
        }
        return false
    }
    else return true
}

function alleFelderGefuellt(){
    let runden_inputs = document.getElementsByClassName('rundeninput')
    let alle_inputs_gefüllt = true;
    for(const input of runden_inputs){
        if(input.value == ''){alle_inputs_gefüllt=false}
    }
    return alle_inputs_gefüllt
}

function reset_inputs(){
    let runden_inputs = document.getElementsByClassName('rundeninput')
    for(const input of runden_inputs){
        input.value = ''
    }
}

function disableSubmitButton(){
    let submitButton = document.getElementById('submitRundeButton')
    submitButton.classList.remove('disabled')
    submitButton.className += ' disabled'
}

function enableSubmitButton(){
    let submitButton = document.getElementById('submitRundeButton')
    submitButton.classList.remove('disabled')
}

function baue_neu_gesamtpunktzahl(){
    for(let i in partie.spieler){
        let punktzahl = document.getElementById(`punkte${i}`)
        punktzahl.innerText = partie.punktetabelle[partie.letzte_runde][i]
        
        
        if(partie.punktetabelle[partie.letzte_runde][i] == partie.punktetabelle[partie.letzte_runde].reduce((a, b) => Math.max(a, b), -Infinity)){
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



function activateSubmitButtonIfInputsValid(){
    let inputs_valide = false

    if(alleFelderGefuellt()){
        inputs_valide = true

        if(partie.regeln=='Turnier'){
        inputs_valide = checkInputsForTurnierregeln()
        }
    }

    if(inputs_valide){
        enableSubmitButton()
    }
    else disableSubmitButton()
}

function checkInputsForTurnierregeln(){
    let inputs_valide = true

    if(!alleFelderGefuellt()){throw new Error('Something went wrong')}

    
    inputs_valide = inputs_valide & checkStichzahlGleichRundenzahl()
    
    if(partie.aktuelle_runde >= 2){
        inputs_valide = inputs_valide & checkSchaetzungenUngleichRundenzahl()
    }

    return inputs_valide


}

function checkStichzahlGleichRundenzahl(){
    let stichsumme = 0 
    let stiche_inputs = document.getElementsByClassName('stichinput')
    for(const i of stiche_inputs){
        if(i.value != ''){stichsumme += Number(i.value)}
    }
    return stichsumme == partie.aktuelle_runde
}

function checkSchaetzungenUngleichRundenzahl(){
    let schaetzungensumme = 0 
    let schaetzungen_inputs = document.getElementsByClassName('schaetzunginput')
    for(const i of schaetzungen_inputs){
        if(i.value != ''){schaetzungensumme += Number(i.value)}
    }
    return schaetzungensumme != partie.aktuelle_runde 
}


function ersetzeImputContainerMitEndstandContainer(){
    let pagerow = document.getElementById('InputContainer').parentElement
    pagerowcode = `
          <div id="EndstandContainer" class="container sticky-top text-center p-2 row fancy-bg" style="max-width: 100vw;">
            <div class="row">`
    pagerowcode += EndstandSpaltePlatzierungen()
    pagerowcode += EndstandSpalteSpieler()
    pagerowcode += EndstandSpaltePartiepunkte()
    if(partie.regeln=='Turnier') {
        pagerowcode += EndstandSpalteTurnierpunkte()
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
    


function EndstandSpaltePlatzierungen(){
    code = `
            <div id='platzierungenspalte' class='endstandspalte'>
              <div class='endstandspaltenheader'>
                Platz
              </div>`
    for(i of range(partie.spieler.length))
        code += `
              <div id='platz${i+1}' class="endstandspaltenelement">
                ${i+1}
              </div>`
    code += `
    </div>`

    return code
}

function EndstandSpalteSpieler(){
    code = `
            <div id='spielerspalte' class='endstandspalte'>
              <div class='endstandspaltenheader'>
                Spieler
              </div>`
    platzierungen = ermittle_platzierungen(partie)
    for(i of range(partie.spieler.length)){
        spielerindex = platzierungen.findIndex(p => p == i+1)
        code += `
              <div id='spielerplatz${i+1}' class="endstandspaltenelement">
                ${partie.spieler[spielerindex]}
              </div>`
        }
    code += `
    </div>`

    return code
}

function EndstandSpaltePartiepunkte(){
    code = `
            <div id='ppspalte' class='endstandspalte'>
              <div class='endstandspaltenheader'>
                Partiepunkte
              </div>`
    platzierungen = ermittle_platzierungen(partie)
    for(i of range(partie.spieler.length)){
        spielerindex = platzierungen.findIndex(p => p == i+1)
        code += `
              <div id='ppplatz${i+1}' class="endstandspaltenelement">
                ${partie.punktetabelle[partie.letzte_runde][spielerindex]}
              </div>`
        }
    code += `
    </div>`

    return code
}

function EndstandSpalteTurnierpunkte(){
    code = `
            <div id='ppspalte' class='endstandspalte'>
              <div class='endstandspaltenheader'>
                Turnierpunkte
              </div>`
    for(i of range(partie.spieler.length)){
        code += `
              <div id='tpplatz${i+1}' class="endstandspaltenelement">
                ${turnierpunkte(i+1)}
              </div>`
        }
    code += `
    </div>`

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
                <div id="Spielernamen" class="" data-bs-toggle="tooltip" data-bs-placement="right" data-bs-title="Name">
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
            console.log(partie.aktuelle_runde == undefined)


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


TestLadeEndstand()








////////////////// Führe aus

/*


const rundenzahlen_ohne_ende = [,,,[2,4,5,6,7,8,9,10,11,12],[1,3,5,7,9,11,12,13,14,15], [2,4,6,8,10,12,14,16,18,20]
        ]


*/

