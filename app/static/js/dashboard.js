socket.on("newdashboard", updateEnergy);

///////////////////////////////////////
// UPDATE when new measures received //
///////////////////////////////////////
function updateEnergy(new_kw, new_today_kw, new_week_kw, new_month_kw, measures_devices) {
    // General values    
    var mean = new_kw*1000/5;

    var kw_actual = document.getElementById("kw_actual");
    kw_actual.innerHTML = new_kw + " kW";
    
    var kw_today = document.getElementById("kw_today");
    kw_today.innerHTML = new_today_kw + " kWh";

    var kw_week = document.getElementById("kw_week");
    kw_week.innerHTML = new_week_kw + " kWh";

    var kw_month = document.getElementById("kw_month");
    kw_month.innerHTML = new_month_kw + " kWh";

    var fridge = document.getElementById("pfridge");
    fridge.innerHTML = deviceValue(measures_devices["Frigo"],mean);
    
    var hob = document.getElementById("phob");
    hob.innerHTML = deviceValue(measures_devices["Taque de cuisson"],mean);

    var dishw = document.getElementById("pdishwasher");
    dishw.innerHTML = deviceValue(measures_devices["Lave-vaisselle"],mean);

    var light = document.getElementById("plight");
    light.innerHTML = deviceValue(measures_devices["Lampe"],mean);

    var boil = document.getElementById("pboil");
    boil.innerHTML = deviceValue(measures_devices["Bouilloire"],mean);
}

function deviceValue(deviceValue, mean) {
    if (deviceValue > mean) {
        return "🔴 " + deviceValue + " W"
    }
    return "🟢 " + deviceValue + " W"
}