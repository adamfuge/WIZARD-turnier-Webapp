

function aktueller_stand(){

    fetch('/tournament_data', {
    method: 'GET'
    })
    .then(response => {
        // Check if the server actually returned a 200 OK status
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        console.log('hi');
        return response.json(); // Parses JSON automatically
    })
    .then(data => {
        console.log('Success parsed data:', data);
        console.log('ho');
        console.log(JSON.parse(data));
    })
    .catch((error) => {
        console.error('Error fetching or parsing data:', error);
    });

}


function baueTurniertabelle(){



    //GET the Turnierdaten
    fetch('/tournament_data')
    .then(response => response.text())
    .then(data => {
        console.log('Success:', data);
        console.log(JSON.parse(data));

        let punktetabelle = document.getElementById("blockContainer")
        let tabellencode = `<div class="scrolling-content scrolling">`

        for(const item of JSON.parse(data)){
            tabellencode += baueReihe(item)
        }
        //tabellencode += `</div>`
        punktetabelle.innerHTML += tabellencode

        punktetabelle.addEventListener("click", changeScrolling)
    })
    .catch((error) => {
        console.error('Error:', error);
        

    })
}   


function baueReihe(item){
    let reihe = `
        <div class="row centered">
        <div class="turnierstandzeile status-${item.status} style="width: 10 vw;"> 
          <div class="turnierstandelement" style="width: 10vw;">
            <div class="platzierung turnierstandinfo" style="font-weight: bold">
                ${item.rank}.
            </div>
            <div class='turnierstanddetail'>
                Platz
            </div>
          </div>
        </div>

        <div class="turnierstandzeile status-${item.status} "> 
          <div class='turnierstandelement'>
          
          <div class='turnierstanddetail'>
          Spieler
          </div>
          <div class="spieler turnierstandinfo" style="font-weight: bold">
          ${item.spieler}
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
          ${item.EP}
          </div>
          <div class='turnierstanddetail'>
          Erfahrungspunkte
          </div>
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

function stopScrolling(){
    scrolling = document.getElementsByClassName("scrolling")
    scrolling[0].classList.remove("scrolling-content")


}

function startScrolling(){
    scrolling = document.getElementsByClassName("scrolling")
    scrolling[0].className += " scrolling-content"
}

function changeScrolling(){
    scrolling = document.getElementsByClassName("scrolling")
    if(scrolling[0].classList.contains("scrolling-content"))
        stopScrolling()
    else 
        startScrolling()

}



















baueTurniertabelle()