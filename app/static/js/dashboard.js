socket.on("newdashboard", updateEnergy);

///////////////////////////////////////
// UPDATE when new measures received //
///////////////////////////////////////
function updateEnergy(new_kw, new_today_kw) {
    // General values    
    var kw_actual = document.getElementById("kw_actual");
    kw_actual.innerHTML = new_kw + " kW";
    
    var kw_today = document.getElementById("kw_today");
    kw_today.innerHTML = new_today_kw + " kWh";
}
