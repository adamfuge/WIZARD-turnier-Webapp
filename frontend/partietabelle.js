import * as pb from 'partieberechnungen'

const rundenzahlen = [, , , [2, 4, 5, 6, 7, 8, 9, 10, 11, 12], [1, 3, 5, 7, 9, 11, 12, 13, 14, 15], [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]]

/**
 * Konstruiert die gesamte Punktetabelle als HTML und rendert sie
 * @param {object} currentPartie - Das aktuelle Partie-Objekt
 */
export function bauePunktetabelle(currentPartie) {
  const punktetabelle = document.getElementById('ResultsContainer')
  let tabellencode = ''
  for (const runde of rundenzahlen[currentPartie.spieler.length]) {
    tabellencode += `<div class="row">${baueReihe(currentPartie, runde)}</div>`
  }
  punktetabelle.innerHTML = tabellencode
}

/**
 * Baut eine einzelne Reihe der Punktetabelle
 * @param {object} currentPartie - Das aktuelle Partie-Objekt
 * @param {number} runde - Die Rundennummer
 * @returns {string} HTML der Tabellenreihe
 */
function baueReihe(currentPartie, runde) {
  if (currentPartie.punktetabelle[runde] == undefined) {
    return baueLeereReihe(runde)
  }
  return baueVolleReihe(currentPartie, runde)
}

/**
 * Baut eine leere Reihe (für noch nicht gespielte Runden)
 * @param {number} runde - Die Rundennummer
 * @returns {string} HTML der leeren Tabellenreihe
 */
function baueLeereReihe(runde) {
  return `<div class="col-1 align-self-center p-0" style="font-weight: bold">${runde}</div>
          <div class="col-11 align-content-center p-0 pe-2">
            <div id="cardPlaceholder${runde}" class="container card p-1">
              <div class="row" id="resultRow${runde}"></div>
            </div>
          </div>`
}

/**
 * Baut eine vollständige Reihe mit Spielerdaten
 * @param {object} currentPartie - Das aktuelle Partie-Objekt
 * @param {number} runde - Die Rundennummer
 * @returns {string} HTML der gefüllten Tabellenreihe
 */
function baueVolleReihe(currentPartie, runde) {
  let reihe = `<div class="col-1 align-self-center p-0" style="font-weight: bold">${runde}</div>
               <div class="col-11 align-content-center p-0 pe-2">
                 <div id="cardPlaceholder${runde}" class="container">
                   <div class="row" id="resultRow${runde}">`
  for (const spielerindex of pb.range(currentPartie.spieler.length)) {
    reihe += baueVolleReiheElement(currentPartie, runde, spielerindex)
  }
  reihe += `       </div>
                 </div>
               </div>`
  return reihe
}

/**
 * Baut ein einzelnes Element (Spieler-Karte) in einer Tabellenreihe
 * @param {object} currentPartie - Das aktuelle Partie-Objekt
 * @param {number} runde - Die Rundennummer
 * @param {number} spielerindex - Der Index des Spielers
 * @returns {string} HTML der Spieler-Karte
 */
function baueVolleReiheElement(currentPartie, runde, spielerindex) {
  const isMatch = currentPartie.schaetzungen[runde][spielerindex] == currentPartie.stiche[runde][spielerindex]
  return `<div class="col p-1">
            <div class="card">
              <div class="row" data-bs-toggle="tooltip" data-bs-placement="top" data-bs-title="${currentPartie.spieler[spielerindex]}">
                <div class="col-8 align-self-center p-1">
                  <span class="position-relative">
                    ${currentPartie.punktetabelle[runde][spielerindex]}
                    <span class="position-absolute top-50 start-100 translate-middle" style="padding-left: 20px">
                      ${currentPartie.geber[runde] == currentPartie.spieler[spielerindex] ? `<i class="bi-files"></i>` : ``}
                    </span>
                  </span>
                </div>
                <div class="col-4 p-1">
                  <div class="col-12">
                    <span class="bid ${isMatch ? `bold matchColor` : ``}">${currentPartie.schaetzungen[runde][spielerindex]}</span>
                  </div>
                  <div class="col-12">
                    <span class="actual ${isMatch ? `bold matchColor` : ``}">${currentPartie.stiche[runde][spielerindex]}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>`
}
