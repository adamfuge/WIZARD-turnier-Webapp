import * as pb from './partieberechnungen.js'


const rundenzahlen = [,,,[2,4,5,6,7,8,9,10,11,12],[1,3,5,7,9,11,12,13,14,15], [2,4,6,8,10,12,14,16,18,20]
        ]




let partie = pb.new_partie('A',[1,2,3,4])

pb.update_partie(partie,pb.schaetzungen,pb.stiche)


console.log(partie)

bauePunktetabelle(partie)

function bauePunktetabelle(partie){
    let punktetabelle = document.getElementById("ResultsContainer")
    let tabellencode = ``
    for(const i of rundenzahlen[partie.spieler.length]){
        
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
    for(const spielerindex of pb.range(partie.spieler.length)){
        reihe += baueVolleReiheElement(partie,reihenzahl,spielerindex)
    }           
    reihe += `
              </div>
            </div>
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

function submitRunde(){
    console.log('test')
    // Entnehme Eingaben

    // Prüfe eingaben

    // Update Partie
    pb.update_partie(partie,pb.schaetzungen,pb.stiche)

    // Baue die Punktetabelle neu
    neubauePunktetabelle(partie)

}

function neubauePunktetabelle(partie){
    let punktetabelle = document.getElementById("ResultsContainer")
    let neue_punktetabelle = document.createElement("div")
    neue_punktetabelle.id = "ResultsContainer"
    neue_punktetabelle.class = "container text-center card bg-light ps-1 pe-2 pt-2 pb-2"
    punktetabelle.replaceWith(neue_punktetabelle)

}

function test(){console.log('test')}
