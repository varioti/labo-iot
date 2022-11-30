socket.on("update", update);

///////////////////////////////////////
// UPDATE when new measures received //
///////////////////////////////////////
function update(is_open, temp_in, temp_out, hum, current, mode_auto) {
    // General values    
    var h_temp_in = document.getElementById("temp_in");
    var h_temp_out = document.getElementById("temp_out");
    var h_hum = document.getElementById("hum");
    var state = document.getElementById("state");

    h_temp_in.innerHTML = temp_in.toFixed(1) + "°C";
    h_temp_out.innerHTML = temp_out.toFixed(1) + "°C";
    h_hum.innerHTML = hum.toFixed(2) + "%";
    state.innerHTML = current;

    // Mode auto of the window
    var auto_button = document.getElementById("auto");
    var auto_info = document.getElementById("auto_info");

    if (mode_auto) {
        auto_button.innerHTML = "Désactiver";
        auto_info.innerHTML = "🟢 Auto";
    } else {
        auto_button.innerHTML = "Activer";
        auto_info.innerHTML = "🔴 Manuelle";
    }

    // Window open or not
    var window_info = document.getElementById("open_info");
    var window_img = document.getElementById("window_img");
    var open_button = document.getElementById("open");
    if (is_open) {
        window_info.innerHTML = "Ouverte"
        window_img.src = "../static/image/window_open.jpg"
        window_img.alt = "open"

        open_button.innerHTML = "Fermer"
        open_button.href = "/close/"
    } else {
        window_info.innerHTML = "Fermée"
        window_img.src = "../static/image/window_close.jpg"
        window_img.alt = "closed"

        open_button.innerHTML = "Ouvrir"
        open_button.href = "/open/"
    }

    reason_open();
}

function reason_open() {
    // General values    
    var temp_in = parseFloat(document.getElementById("temp_in").innerHTML.slice(0, -2));
    var temp_out = parseFloat(document.getElementById("temp_out").innerHTML.slice(0, -2));
    var state = document.getElementById("state").innerHTML;

    var reason = document.getElementById("reason");
    reason.innerHTML = "";

    if (state.includes("Refroidir")) {
        reason.innerHTML = reason.innerHTML + "La température de la pièce est trop haute et il fait plus froid dehors.";
    }

    if (state.includes("Chauffer")) {
        reason.innerHTML = reason.innerHTML + "La température de la pièce est trop basse et il fait plus chaud dehors.";
    }

    if (state.includes("Déshumidifier")) {
        if (temp_out < temp_in) {
            reason.innerHTML = reason.innerHTML + "Un air chargé d’eau sera plus difficile à chauffer qu’un air sec.<br>" ;
        } else {
            reason.innerHTML = reason.innerHTML + "Un air humide favorise le développement des moisissures et des micro-organismes comme les acariens.<br>";
        }
    }
    
    if (state == "Déshumidifier" && Math.abs(temp_in-temp_out) > 2) {
        reason.innerHTML = reason.innerHTML + "La fenêtre est ouverte pendant 10 minutes pour éviter d'impacter la température de la pièce.<br>";
    }
}

reason_open();
