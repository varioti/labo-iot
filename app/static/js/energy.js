const socket = io();
socket.on("newmeasure", newmeasure);

///////////////////////////////////////
// UPDATE when new measures received //
///////////////////////////////////////
function newmeasure(names, measures) {
    let measures_tables = document.getElementById("measures_tables");
    while (measures_tables.firstChild) {
        measures_tables.removeChild(measures_tables.lastChild);
    }
    
    for (let i=0; i < names.length; i++) {
        let table = document.createElement('table');
        table.display = "inline-block";
        let head = table.insertRow(0);
        let head1 = head.insertCell(0);
        let head2 = head.insertCell(1);
        head1.innerHTML = names[i]
        head2.innerHTML = "Mesure"
        
        for (let j=0; j < measures[i].length; j++) {
            let row = table.insertRow(1);
            let cell1 = row.insertCell(0);
            let cell2 = row.insertCell(1);
            cell1.innerHTML = measures[i][j]["datetime"]
            cell2.innerHTML = measures[i][j]["measure"]
        }
        measures_tables.appendChild(table);
    }

}
