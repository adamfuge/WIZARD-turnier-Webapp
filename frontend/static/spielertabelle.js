


let spielerergebnisse = [
    {tisch:'A', spieler:35, TP: 45, PP:550, anzahl_richtige_ansagen: 10, zeitpunkt: 783333333 },
    {tisch:'I', spieler:35, TP: 5, PP:-100, anzahl_richtige_ansagen: 5, zeitpunkt: new Date()},
    {tisch:'M', spieler:35, TP: 0, PP:-1230, anzahl_richtige_ansagen: 0, zeitpunkt: 784844444},
]

spielerergebnisse = []

function baueSpielertabelle(){
    let punktetabelle = document.getElementById("blockContainer")
    let tabellencode = ``

    if(spielerergebnisse.length == 0) tabellencode = 'Keine Spielergebnisse gefunden' 
    else
    for(const item of spielerergebnisse){
        tabellencode += baueReihe(item)
    }

    punktetabelle.innerHTML += tabellencode
}


function baueReihe(item){
    let stunde = new Date(item.zeitpunkt).getHours()
    let minute = new Date(item.zeitpunkt).getMinutes()
    let reihe = `
        <div class="turnierstandzeile"> 
          <div class='turnierstandelement'>
          <div class="turnierpunktzahl turnierstandinfo" style="font-weight: bold">
          ${item.TP}
          </div>
          <div class='turnierstanddetail'>
          TP
          </div>
          </div>
          <div class='turnierstandelement'>

          <div class="partiepunktzahl turnierstandinfo" style="font-weight: bold">
          ${item.PP}
          </div>
          <div class='turnierstanddetail'>
          PP
          </div>
          </div>
          <div class='turnierstandelement laenger'>

          <div class="ansagenanzahl turnierstandinfo" style="font-weight: bold">
          ${item.anzahl_richtige_ansagen}
          </div>
          <div class='turnierstanddetail laenger'>
          Ansagen richtig
          </div>
          </div>
          <div class='turnierstandelement'>

          <div class="tisch turnierstandinfo" style="font-weight: bold">
          ${item.tisch}
          </div>
          <div class='turnierstanddetail'>
          Tisch
          </div>
          </div>

          <div class='turnierstandelement'>
          <div class="zeitpunkt turnierstandinfo" style="font-weight: bold">
          ${(stunde<10 ? '0':'')+stunde}:${(minute<10 ? '0':'')+minute}
          </div>
          <div class='turnierstanddetail'>
          Zeit
          </div>
          </div>
        </div>`
    return reihe
}



function resetSpielerErgebnisse(){
    aktuellerSpielerinfo = document.getElementById('aktuellerSpielerinfo')
    aktuellerSpielerinfo.innerHTML = ''

    blockContainer = document.getElementById('blockContainer')
    blockContainer.innerHTML= ''
    blockContainer.className += ' hide'
}

spielernameninput = document.getElementById('spielernameninput')
spielernameninput.oninput = function(){
    resetSpielerErgebnisse()

    if(spielernameninput.value != ''){
        
        if(!isPositiveInteger(spielernameninput.value) | 0 == spielernameninput.value){
            spielernameninput.value = spielernameninput.value.substring(0, spielernameninput.value.length - 1);
            //wenn nicht erfolgreich, lösche eingabe
            if(!isPositiveInteger(spielernameninput.value) | 0 == spielernameninput.value){
                spielernameninput.value = ''
            }
        }
        spielernameninput.value = Number(spielernameninput.value)
        
        baueSpielerinfo(spielernameninput.value)

        /*
        //GET the spielergebnisse von einem Spieler from the backend
        fetch('/get_player_matches', {
            method: 'POST',
            body: spielernameninput.value,
        })
        .then(response => response.text())
        .then(data => {
            console.log('Success:', data);
            spielerergebnisse = data
        })
        .catch((error) => {
            console.error('Error:', error);
            spielerergebnisse = []

        });
        */

        // Zum testen
        if(spielernameninput.value == 35){spielerergebnisse = [
        {tisch:'A', spieler:35, TP: 45, PP:550, anzahl_richtige_ansagen: 10, zeitpunkt: 783333333 },
        {tisch:'I', spieler:35, TP: 5, PP:-100, anzahl_richtige_ansagen: 5, zeitpunkt: new Date()},
        {tisch:'M', spieler:35, TP: 0, PP:-1230, anzahl_richtige_ansagen: 0, zeitpunkt: 784844444},
        ]}
        else spielerergebnisse = []

        baueSpielertabelle()
    }

    



}   

function baueSpielerinfo(spieler){
    aktuellerSpielerinfo = document.getElementById('aktuellerSpielerinfo')
    aktuellerSpielerinfo.innerHTML = `Ergebnisse von Spieler ${spieler}:`
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

function reset_inputs(){
    let runden_inputs = document.getElementsByClassName('rundeninput')
    for(const input of runden_inputs){
        input.value = ''
    }
}







resetSpielerErgebnisse()

