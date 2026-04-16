



function baueTurniertabelle(){


    data = getTabellendata()

    let punktetabelle = document.getElementById("blockContainer")
    let tabellencode = `<div id="scrollContainer" class="isscrolling">`
    for(const item of data){
        tabellencode += baueReihe(item)
    }
    tabellencode += "</div>"
    punktetabelle.innerHTML += tabellencode

        

}


function baueReihe(item){
    let reihe = `
        <div class="row" style="justify-content: center">
        <div class="turnierstandzeile status-${item.status}"> 
          <div class='turnierstandelement' style="width: 10vw">
            <div class="platzierung turnierstandinfo" style="font-weight: bold">
            ${item.rank}.
            </div>
            <div class='turnierstanddetail'>
            Platz
            </div>
          </div>
        </div>
        <div class="turnierstandzeile status-${item.status}"> 
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



function stopScrolling(){

}




function getTabellendata(){
    return[

{rank: 1,spieler: 58,TP: 110,EP: 1100,status: "qualifiziert"},{rank: 2,spieler: 46,TP: 105,EP: 1300,status: "qualifiziert"},{rank: 3,spieler: 68,TP: 105,EP: 1300,status: "qualifiziert"},{rank: 4,spieler: 21,TP: 95,EP: 4600,status: "qualifiziert"},{rank: 5,spieler: 56,TP: 95,EP: 1900,status: "qualifiziert"},{rank: 6,spieler: 59,TP: 95,EP: 1800,status: "qualifiziert"},{rank: 7,spieler: 15,TP: 95,EP: 1710,status: "qualifiziert"},{rank: 8,spieler: 81,TP: 95,EP: 1600,status: "qualifiziert"},{rank: 9,spieler: 93,TP: 95,EP: 1500,status: "qualifiziert"},{rank: 10,spieler: 26,TP: 95,EP: 1500,status: "qualifiziert"},{rank: 11,spieler: 87,TP: 95,EP: 1400,status: "qualifiziert"},{rank: 12,spieler: 40,TP: 95,EP: 1310,status: "qualifiziert"},{rank: 13,spieler: 75,TP: 95,EP: 1210,status: "none"},{rank: 14,spieler: 4,TP: 95,EP: 1200,status: "none"},{rank: 15,spieler: 60,TP: 95,EP: 1200,status: "none"},{rank: 16,spieler: 77,TP: 95,EP: 1200,status: "none"},{rank: 17,spieler: 97,TP: 95,EP: 1200,status: "none"},{rank: 18,spieler: 17,TP: 95,EP: 1200,status: "none"},{rank: 19,spieler: 5,TP: 95,EP: 1110,status: "none"},{rank: 20,spieler: 6,TP: 95,EP: 1100,status: "none"},{rank: 21,spieler: 13,TP: 95,EP: 1100,status: "none"},{rank: 22,spieler: 65,TP: 95,EP: 1100,status: "none"},{rank: 23,spieler: 22,TP: 95,EP: 1010,status: "none"},{rank: 24,spieler: 19,TP: 95,EP: 1010,status: "none"},{rank: 25,spieler: 90,TP: 95,EP: 910,status: "none"},{rank: 26,spieler: 29,TP: 95,EP: 910,status: "none"},{rank: 27,spieler: 36,TP: 85,EP: 6900,status: "none"},{rank: 28,spieler: 30,TP: 85,EP: 1800,status: "none"},{rank: 29,spieler: 38,TP: 85,EP: 1750,status: "none"},{rank: 30,spieler: 73,TP: 85,EP: 1450,status: "none"},{rank: 31,spieler: 82,TP: 85,EP: 1410,status: "none"},{rank: 32,spieler: 48,TP: 85,EP: 1200,status: "none"},{rank: 33,spieler: 86,TP: 85,EP: 1150,status: "none"},{rank: 34,spieler: 42,TP: 85,EP: 1150,status: "none"},{rank: 35,spieler: 64,TP: 85,EP: 1150,status: "none"},{rank: 36,spieler: 8,TP: 85,EP: 1150,status: "none"},{rank: 37,spieler: 63,TP: 85,EP: 1150,status: "none"},{rank: 38,spieler: 94,TP: 85,EP: 1100,status: "none"},{rank: 39,spieler: 33,TP: 85,EP: 1100,status: "none"},{rank: 40,spieler: 2,TP: 85,EP: 1100,status: "none"},{rank: 41,spieler: 16,TP: 85,EP: 1050,status: "none"},{rank: 42,spieler: 74,TP: 85,EP: 1050,status: "none"},{rank: 43,spieler: 72,TP: 85,EP: 1050,status: "none"},{rank: 44,spieler: 88,TP: 85,EP: 1050,status: "none"},{rank: 45,spieler: 1,TP: 85,EP: 1050,status: "none"},{rank: 46,spieler: 37,TP: 85,EP: 1050,status: "none"},{rank: 47,spieler: 54,TP: 85,EP: 1050,status: "none"},{rank: 48,spieler: 51,TP: 85,EP: 1000,status: "none"},{rank: 49,spieler: 35,TP: 85,EP: 960,status: "none"},{rank: 50,spieler: 89,TP: 85,EP: 960,status: "none"},{rank: 51,spieler: 47,TP: 85,EP: 960,status: "none"},{rank: 52,spieler: 11,TP: 85,EP: 910,status: "none"},{rank: 53,spieler: 96,TP: 85,EP: 910,status: "none"},{rank: 54,spieler: 45,TP: 85,EP: 860,status: "none"},{rank: 55,spieler: 18,TP: 85,EP: 860,status: "none"},{rank: 56,spieler: 69,TP: 80,EP: 900,status: "none"},{rank: 57,spieler: 31,TP: 75,EP: 4710,status: "none"},{rank: 58,spieler: 61,TP: 75,EP: 1800,status: "none"},{rank: 59,spieler: 24,TP: 75,EP: 1800,status: "none"},{rank: 60,spieler: 102,TP: 75,EP: 1400,status: "none"},{rank: 61,spieler: 84,TP: 75,EP: 1350,status: "none"},{rank: 62,spieler: 52,TP: 75,EP: 1160,status: "none"},{rank: 63,spieler: 101,TP: 75,EP: 1100,status: "none"},{rank: 64,spieler: 67,TP: 75,EP: 1100,status: "none"},{rank: 65,spieler: 55,TP: 75,EP: 1050,status: "none"},{rank: 66,spieler: 10,TP: 75,EP: 1000,status: "none"},{rank: 67,spieler: 92,TP: 75,EP: 1000,status: "none"},{rank: 68,spieler: 23,TP: 75,EP: 1000,status: "none"},{rank: 69,spieler: 14,TP: 75,EP: 950,status: "none"},{rank: 70,spieler: 44,TP: 75,EP: 860,status: "none"},{rank: 71,spieler: 71,TP: 75,EP: 860,status: "none"},{rank: 72,spieler: 50,TP: 75,EP: 810,status: "none"},{rank: 73,spieler: 34,TP: 75,EP: 800,status: "none"},{rank: 74,spieler: 49,TP: 75,EP: 760,status: "none"},{rank: 75,spieler: 12,TP: 75,EP: 760,status: "none"},{rank: 76,spieler: 62,TP: 70,EP: 800,status: "none"},{rank: 77,spieler: 85,TP: 65,EP: 800,status: "none"},{rank: 78,spieler: 28,TP: 65,EP: 800,status: "none"},{rank: 79,spieler: 104,TP: 65,EP: 800,status: "none"},{rank: 80,spieler: 66,TP: 60,EP: 1600,status: "none"},{rank: 81,spieler: 43,TP: 60,EP: 1450,status: "none"},{rank: 82,spieler: 98,TP: 60,EP: 1300,status: "none"},{rank: 83,spieler: 41,TP: 60,EP: 950,status: "none"},{rank: 84,spieler: 70,TP: 60,EP: 950,status: "none"},{rank: 85,spieler: 9,TP: 60,EP: 900,status: "none"},{rank: 86,spieler: 39,TP: 60,EP: 900,status: "none"},{rank: 87,spieler: 7,TP: 60,EP: 850,status: "none"},{rank: 88,spieler: 83,TP: 60,EP: 800,status: "none"},{rank: 89,spieler: 3,TP: 60,EP: 750,status: "none"},{rank: 90,spieler: 78,TP: 60,EP: 750,status: "none"},{rank: 91,spieler: 53,TP: 60,EP: 750,status: "none"},{rank: 92,spieler: 20,TP: 60,EP: 700,status: "none"},{rank: 93,spieler: 25,TP: 60,EP: 700,status: "none"},{rank: 94,spieler: 27,TP: 60,EP: 700,status: "none"},{rank: 95,spieler: 79,TP: 60,EP: 700,status: "none"},{rank: 96,spieler: 32,TP: 60,EP: 650,status: "none"},{rank: 97,spieler: 76,TP: 60,EP: 650,status: "none"},{rank: 98,spieler: 80,TP: 50,EP: 910,status: "none"},{rank: 99,spieler: 91,TP: 50,EP: 800,status: "none"},{rank: 100,spieler: 99,TP: 50,EP: 600,status: "none"},{rank: 101,spieler: 100,TP: 50,EP: 600,status: "none"},{rank: 102,spieler: 95,TP: 50,EP: 550,status: "none"}



]

}


















baueTurniertabelle()


