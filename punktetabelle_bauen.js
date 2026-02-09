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
                    <div class="row"> 
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
    return `<div class="col-1 align-self-center p-0" style="font-weight: bold">
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
          <div class="col-1 align-self-center p-0" style="font-weight: bold">
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
                <div class="col-3 p-1">
                  <div class="card">
                    <div class="row" data-bs-toggle="tooltip" data-bs-placement="top" data-bs-title="${partie.spieler[spielerindex]}">
                      <div class="col-8 align-self-center p-1">
                        <span class="position-relative">
                          ${partie.punktetabelle[runde][spielerindex]}
                          <span class="position-absolute top-50 start-100 translate-middle" style="padding-left: 20px">
                            ${partie.geber[runde]==partie.spieler[spielerindex] ? `<i class="bi-files"></i>`:``}
                          </span>
                        </span>
                      </div>
                      <div class="col-2 p-1">
                        <div class="col-12">
                          <span class="bid ${partie.schaetzungen[runde][spielerindex] == partie.stiche[runde][spielerindex] ? `bold matchColor`:``}">
                            ${partie.schaetzungen[runde][spielerindex]}
                          </span>
                        </div>
                        <div class="col-12">
                          <span class="actual ${partie.schaetzungen[runde][spielerindex] == partie.stiche[runde][spielerindex] ? `bold matchColor`:``}">
                            ${partie.stiche[runde][spielerindex]}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>`
}
