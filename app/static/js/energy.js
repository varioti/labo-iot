socket.on("updatedevices", updateDevice);

///////////////////////////////////////
// UPDATE device page when new measures received //
///////////////////////////////////////
function updateDevice(summary_devices, measures_devices) {
    var device_name = document.querySelector('meta[name="device_name"]').content;

    var kw_actual = document.getElementById("kw_actual");
    kw_actual.innerHTML = measures_devices[device_name] + " W";
    
    var kw_today = document.getElementById("kw_today");
    kw_today.innerHTML = summary_devices[device_name]["today"] + " kWh";

    var kw_week = document.getElementById("kw_week");
    kw_week.innerHTML = summary_devices[device_name]["week"] + " kWh";

    var kw_month = document.getElementById("kw_month");
    kw_month.innerHTML = summary_devices[device_name]["month"] + " kWh";

}