import * as pb from './partieberechnungen.js'

const rundenzahlen = [,,,[2, 4, 5, 6, 7, 8, 9, 10, 11, 12],[1, 3, 5, 7, 9, 11, 12, 13, 14, 15],[2, 4, 6, 8, 10, 12, 14, 16, 18, 20]]

let partie
let undoHistory = []

function initPartie() {
    const playerNames = getPlayerNames()
    partie = pb.new_partie('A', playerNames)
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

function clonePartie(source) {
    if (typeof structuredClone === 'function') {
        return structuredClone(source)
    }
    return JSON.parse(JSON.stringify(source))
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

function collectInputValues(prefix) {
    const values = []
    let valid = true

    for (const i of pb.range(partie.spieler.length)) {
        const input = document.getElementById(`${prefix}${i + 1}`)
        const fieldValid = validateInput(input)
        if (!fieldValid) {
            valid = false
        }
        values.push(Number(input.value.trim()))
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
    body.textContent = `Invalid total of actual tricks. The maximum number of tricks to be taken in this round is ${partie.aktuelle_runde}`
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

function load() {
    initPartie()
    clearInputs()
    refreshUI()
}

function submitRound() {
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

function undoRound() {
    if (undoHistory.length === 0) {
        return
    }
    partie = undoHistory.pop()
    clearInputs()
    refreshUI()
}

function validateNumber(inputElement) {
    validateInput(inputElement)
}

function validateNumber2(inputElement) {
    validateInput(inputElement)
}

function sendFeedback() {
    const feedback = document.getElementById('feedbacktext')
    const text = feedback.value.trim()
    if (text.length > 0) {
        console.info('Feedback:', text)
    }
    feedback.value = ''
}

window.load = load
window.submitRound = submitRound
window.undoRound = undoRound
window.validateNumber = validateNumber
window.validateNumber2 = validateNumber2
window.sendFeedback = sendFeedback

load()
