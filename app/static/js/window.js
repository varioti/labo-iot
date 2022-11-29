socket.on("update", update);

///////////////////////////////////////
// UPDATE when new measures received //
///////////////////////////////////////
function update(is_open, temp_in, temp_out, hum, current, mode_auto, log) {
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
}
