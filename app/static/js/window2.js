socket.on("update", update);

///////////////////////////////////////
// UPDATE when new measures received //
///////////////////////////////////////
function update(is_open, temp_in, temp_out, hum, current, mode_auto) {
    var window_info = document.getElementById("window_info");
    var window_img = document.getElementById("window_img");
    var open_button = document.getElementById("open");
    var auto_button = document.getElementById("auto");
    var myTable = document.getElementById("measures");

    if (mode_auto) {
        auto_button.innerHTML = "Désactiver mode auto";
        myTable.rows[3].cells[0].innerHTML = "Action(s) actuelle(s) : ";
    } else {
        auto_button.innerHTML = "Activer mode auto";
        myTable.rows[3].cells[0].innerHTML = "Conseil(s) :";
    }

    if (is_open) {
        window_info.innerHTML = "La fenêtre est ouverte"
        window_img.src = "../static/image/window_open.png"
        window_img.alt = "open"

        open_button.innerHTML = "Fermer"
        open_button.href = "/close/"
    } else {
        window_info.innerHTML = "La fenêtre est fermée"
        window_img.src = "../static/image/window_close.png"
        window_img.alt = "closed"

        open_button.innerHTML = "Ouvrir"
        open_button.href = "/open/"
    }

    myTable.rows[0].cells[1].innerHTML = temp_in.toFixed(1) + " °C";
    myTable.rows[1].cells[1].innerHTML = temp_out.toFixed(1) + " °C";
    myTable.rows[2].cells[1].innerHTML = hum.toFixed(2) + " %";
    myTable.rows[3].cells[1].innerHTML = current;
}
