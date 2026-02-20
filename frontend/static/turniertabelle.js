


turnierstand = [
    {rank: 1, spieler:35, TP: 75, PP:550, status: 'qualifiziert'},
    {rank: 2, spieler:71, TP: 70, PP:-100, status: 'hat_bereits_qualifikation'},
    {rank: 3, spieler:2,  TP: 60, PP:550, status: 'qualifiziert'},
    {rank: 3, spieler:3, TP: 60, PP:550, status: 'qualifiziert'},
    {rank: 5, spieler:1, TP: 20, PP:0, status: 'none'},
    {rank: 6, spieler:99, TP: 20, PP:-8880, status: 'none'},
    {rank: 7, spieler:9, TP: 0, PP:-210, status: 'none'},
    {rank: 8, spieler:11, TP: 0, PP:-210, status: 'none'},
    {rank: NaN, spieler:98, TP: 80, PP:-2010, status: 'disqualifiziert'}

]

function baueTurniertabelle(){
    let punktetabelle = document.getElementById("blockContainer")
    let tabellencode = ``

    for(const item of turnierstand){
        tabellencode += baueReihe(item)
    }
    punktetabelle.innerHTML += tabellencode
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







function neubauePunktetabelle(partie){
    let punktetabelle = document.getElementById("ResultsContainer");
    let neue_punktetabelle = document.createElement("div");
    neue_punktetabelle.id = "ResultsContainer";
    neue_punktetabelle.className = "container text-center card bg-light ps-1 pe-2 pt-2 pb-2";
    punktetabelle.replaceWith(neue_punktetabelle);
    bauePunktetabelle(partie)

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

function disableSubmitButton(){
    let submitButton = document.getElementById('submitRundeButton')
    submitButton.classList.remove('disabled')
    submitButton.className += ' disabled'
}

function enableSubmitButton(){
    let submitButton = document.getElementById('submitRundeButton')
    submitButton.classList.remove('disabled')
}






baueTurniertabelle()