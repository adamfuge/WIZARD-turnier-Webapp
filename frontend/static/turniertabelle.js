



function baueTurniertabelle(){

    //GET the Turnierdaten
    fetch('/tournament_data')
    .then(response => response.text())
    .then(data => {
        console.log('Success:', data);
        console.log(JSON.parse(data));

        let punktetabelle = document.getElementById("blockContainer")
        let tabellencode = ``

        for(const item of JSON.parse(data)){
            tabellencode += baueReihe(item)
        }
        punktetabelle.innerHTML += tabellencode

    })
    .catch((error) => {
        console.error('Error:', error);

        turnierstand = [
        {rank: 1, spieler:35, TP: 75, PP:550, status: 'qualifiziert'},
        {rank: 2, spieler:71, TP: 70, PP:-100, status: 'hat_bereits_qualifikation'},
        {rank: 7, spieler:9, TP: 0, PP:-210, status: 'none'},
        {rank: NaN, spieler:98, TP: 80, PP:-2010, status: 'disqualifiziert'}
        ]

        let punktetabelle = document.getElementById("blockContainer")
        let tabellencode = ``

        for(const item of data){
            tabellencode += baueReihe(item)
        }
        punktetabelle.innerHTML += tabellencode
    });
        

}


function baueReihe(item){
    let reihe = `
        <div class="turnierstandzeile status-${item.status}"> 
          <div class='turnierstandelement'>
          <div class="platzierung turnierstandinfo" style="font-weight: bold">
          ${item.rank}.
          </div>
          <div class='turnierstanddetail'>
          Platz
          </div>
          </div>
          <div class='turnierstandelement'>

          <div class="spieler turnierstandinfo" style="font-weight: bold">
          ${item.spieler}
          </div>
          <div class='turnierstanddetail'>
          Spieler
          </div>
          </div>
          <div class='turnierstandelement'>

          <div class="turnierpunktzahl turnierstandinfo" style="font-weight: bold">
          ${item.TP}
          </div>
          <div class='turnierstanddetail'>
          Turnierpunkte
          </div>
          </div>
          <div class='turnierstandelement'>

          <div class="partiepunktzahl turnierstandinfo" style="font-weight: bold">
          ${item.PP}
          </div>
          <div class='turnierstanddetail'>
          Partiepunkte
          </div>
          </div>
        </div>`
    return reihe
}










function validateNumber(self){

    checkAndCorrectValidInput(self)
    //überprüfe ob alle Felder gefüllt sind und färbe den 'Runde eintragen Knopf'

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


function aufSpielertabelleWeiterleiten(){
    let submitButton = document.getElementById('spielerIDSuche')
    //POST the spielergebnisse to the backend
    

    fetch('/player_view', {
        method: 'GET',
        header: toString(submitButton.value)
    })
    .then(response => response.text())
    .then(data => {
        console.log('Success:', data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
        

}












baueTurniertabelle()


