import * as pb from '../partieberechnungen.js'

const rundenzahlen = [, , , [2, 4, 5, 6, 7, 8, 9, 10, 11, 12], [1, 3, 5, 7, 9, 11, 12, 13, 14, 15], [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]]

let partie
let undoHistory = []

function clonePartie(source) {
  if (typeof structuredClone === 'function') {
    return structuredClone(source)
  }
  return JSON.parse(JSON.stringify(source))
}

function initPartie() {
  // Check if we're on partie.html and have stored partie data
  const storedPartie = localStorage.getItem('currentPartie')
  if (storedPartie && window.location.pathname.includes('partie.html')) {
    const partieData = JSON.parse(storedPartie)
    const playerNames = partieData.spieler
    partie = pb.new_partie(partieData.tisch, playerNames)
    
    // Update table info badge
    const tableInfo = document.getElementById('tableInfo')
    if (tableInfo) {
      tableInfo.textContent = `Tisch: ${partieData.tisch}`
    }
    
    // Update player display
    for (const i of pb.range(playerNames.length)) {
      const el = document.getElementById(`player${i + 1}`)
      if (el) {
        el.childNodes[0].textContent = playerNames[i]
      }
    }
  } else {
    const playerNames = getPlayerNames()
    partie = pb.new_partie('A', playerNames)
  }
  undoHistory = []
}

function getPlayerNames() {
  const names = []
  for (const i of [1, 2, 3, 4]) {
    const el = document.getElementById(`player${i}`)
    const text = el?.childNodes?.[0]?.textContent?.trim() || el?.textContent?.trim() || `P${i}`
    names.push(text)
  }
  return names
}

function bauePunktetabelle(currentPartie) {
  const punktetabelle = document.getElementById('ResultsContainer')
  let tabellencode = ''
  for (const runde of rundenzahlen[currentPartie.spieler.length]) {
    tabellencode += `<div class="row">${baueReihe(currentPartie, runde)}</div>`
  }
  punktetabelle.innerHTML = tabellencode
}

function baueReihe(currentPartie, runde) {
  if (currentPartie.punktetabelle[runde] == undefined) {
    return baueLeereReihe(runde)
  }
  return baueVolleReihe(currentPartie, runde)
}

function baueLeereReihe(runde) {
  return `<div class="col-1 align-self-center p-0" style="font-weight: bold">${runde}</div>
          <div class="col-11 align-content-center p-0 pe-2">
            <div id="cardPlaceholder${runde}" class="container card p-1">
              <div class="row" id="resultRow${runde}"></div>
            </div>
          </div>`
}

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
//chechs ob einen input gibt
function validateInput(inputElement) {
  const value = inputElement.value.trim()
  const round = partie?.aktuelle_runde

  if (value === '') {
    inputElement.classList.remove('is-invalid')
    return false
  }

  const number = Number(value)
  const isValid = Number.isInteger(number) && number >= 0 && Number.isInteger(round) && number <= round
  inputElement.classList.toggle('is-invalid', !isValid)
  return isValid
}

//TODOs ValidateScore


function collectInputValues(prefix) {
  const values = []
  let valid = true

  for (const i of pb.range(partie.spieler.length)) {
    const input = document.getElementById(`${prefix}${i + 1}`)
    const val = input.value.trim()
    if (!val) {
      input.classList.add('is-invalid')
      valid = false
    } else {
      validateInput(input)
      if (input.classList.contains('is-invalid')) {
        valid = false
      }
    }
    values.push(Number(val || 0))
  }

  return valid ? values : null
}

function clearInputs() {
  for (const prefix of ['bid', 'actual']) {
    for (const i of pb.range(partie.spieler.length)) {
      const input = document.getElementById(`${prefix}${i + 1}`)
      input.value = ''
      input.classList.remove('is-invalid')
    }
  }
}

function updateScores() {
  const scoreRow = partie.punktetabelle[partie.letzte_runde] || partie.punktetabelle[0]
  for (const i of pb.range(partie.spieler.length)) {
    const el = document.getElementById(`points${i + 1}`)
    el.textContent = scoreRow[i]
  }
}

function updateRoundInfo() {
  const round = partie.aktuelle_runde
  const roundText = round === 'ende' ? 'Ende' : String(round)

  document.querySelectorAll('.currentRound').forEach((node) => {
    node.textContent = roundText
  })

  const submitRound = document.getElementById('SubmitRound')
  submitRound.textContent = roundText

  const submitButton = document.getElementById('submitRoundButton')
  submitButton.disabled = round === 'ende'
}

function updateDealer() {
  const dealer = partie.aktuelle_runde === 'ende' ? partie.geber[partie.letzte_runde] : partie.geber[partie.aktuelle_runde]

  for (const i of pb.range(partie.spieler.length)) {
    const playerName = partie.spieler[i]
    const nameEl = document.getElementById(`player${i + 1}`)
    nameEl.classList.add('position-relative')
    nameEl.innerHTML = `${playerName}${dealer === playerName ? `<span class="position-absolute top-50 start-100 translate-middle" style="padding-left: 20px"><i class="bi-files"></i></span>` : ''}`
  }
}

function updateUndoButton() {
  const undoButton = document.getElementById('undoButton')
  undoButton.disabled = undoHistory.length === 0
}

function showRuleModal() {
  const body = document.getElementById('modalCheckRuleMaxGuessBody')
  body.textContent = `Ungültige Gesamtzahl der tatsächlichen Stiche. Die maximale Anzahl der Stiche in dieser Runde ist ${partie.aktuelle_runde}`
  if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
    const modalEl = document.getElementById('modalCheckRuleMaxGuess')
    bootstrap.Modal.getOrCreateInstance(modalEl).show()
  }
}

function initTooltips() {
  if (typeof bootstrap === 'undefined' || !bootstrap.Tooltip) {
    return
  }
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach((el) => {
    if (!bootstrap.Tooltip.getInstance(el)) {
      new bootstrap.Tooltip(el)
    }
  })
}

function refreshUI() {
  bauePunktetabelle(partie)
  updateScores()
  updateRoundInfo()
  updateDealer()
  updateUndoButton()
  initTooltips()
}

window.load = function () {
  initPartie()
  clearInputs()
  refreshUI()
}

window.submitRound = function () {
  if (partie.aktuelle_runde === 'ende') {
    return
  }

  const schaetzungen = collectInputValues('bid')
  const stiche = collectInputValues('actual')
  if (!schaetzungen || !stiche) {
    return
  }

  const totalStiche = stiche.reduce((sum, value) => sum + value, 0)
  if (totalStiche > partie.aktuelle_runde) {
    showRuleModal()
    return
  }

  undoHistory.push(clonePartie(partie))
  pb.update_partie(partie, schaetzungen, stiche)
  clearInputs()
  refreshUI()
}

window.undoRound = function () {
  if (undoHistory.length === 0) {
    return
  }
  partie = undoHistory.pop()
  clearInputs()
  refreshUI()
}

window.validateNumber = function (inputElement) {
  validateInput(inputElement)
}

window.validateNumber2 = function (inputElement) {
  validateInput(inputElement)
}

window.sendFeedback = function () {
  const feedback = document.getElementById('feedbacktext')
  const text = feedback.value.trim()
  if (text.length > 0) {
    console.info('Feedback:', text)
  }
  feedback.value = ''
}

window.finishPartie = function () {
  if (partie.aktuelle_runde !== 'ende') {
    alert('Die Partie ist noch nicht zu Ende! Bitte beende alle Runden.')
    return
  }

  // Calculate rankings and tournament points
  const rankings = pb.rankings(partie)
  const turnierpunkte = pb.turnierpunkte(rankings)
  
  // Build ranking display
  const rankingHTML = rankings.map((rank, index) => {
    const spielerIndex = rank[0]
    const spieler = partie.spieler[spielerIndex]
    const partiepunkte = partie.punktetabelle[partie.letzte_runde][spielerIndex]
    const tpunkte = turnierpunkte[index]
    
    return `
      <div class="d-flex justify-content-between align-items-center p-2 ${index < 3 ? 'bg-light' : ''}">
        <div>
          <span class="badge ${index === 0 ? 'bg-warning' : index === 1 ? 'bg-secondary' : index === 2 ? 'bg-danger' : 'bg-light text-dark'}">${index + 1}</span>
          <strong>Spieler ${spieler}</strong>
        </div>
        <div>
          <span class="text-muted">Partiepunkte: ${partiepunkte}</span>
          <span class="badge bg-primary ms-2">+${tpunkte} TP</span>
        </div>
      </div>
    `
  }).join('')
  
  document.getElementById('finalRankingBody').innerHTML = rankingHTML
  
  // Show modal
  if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
    const modalEl = document.getElementById('modalFinishPartie')
    bootstrap.Modal.getOrCreateInstance(modalEl).show()
  }
}

window.confirmFinishPartie = function () {
  // Calculate final results
  const rankings = pb.rankings(partie)
  const turnierpunkte = pb.turnierpunkte(rankings)
  
  const results = rankings.map((rank, index) => {
    const spielerIndex = rank[0]
    return {
      spieler: partie.spieler[spielerIndex],
      partiepunkte: partie.punktetabelle[partie.letzte_runde][spielerIndex],
      turnierpunkte: turnierpunkte[index]
    }
  })
  
  // Load tournament data
  const tournamentData = JSON.parse(localStorage.getItem('tournamentData') || '{"parties": []}')
  
  // Add this partie
  tournamentData.parties.push({
    tisch: partie.tisch,
    timestamp: new Date().toISOString(),
    results: results
  })
  
  // Save
  localStorage.setItem('tournamentData', JSON.stringify(tournamentData))
  
  // Clear current partie
  localStorage.removeItem('currentPartie')
  
  // Hide modal and redirect
  if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
    const modalEl = document.getElementById('modalFinishPartie')
    const modal = bootstrap.Modal.getInstance(modalEl)
    if (modal) modal.hide()
  }
  
  alert('Partie erfolgreich gespeichert!')
  window.location.href = 'turnierstand.html'
}

window.load()
