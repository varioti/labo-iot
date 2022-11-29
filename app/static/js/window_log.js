socket.on("updatelog", updatelog);

/////////////////////////////////
// UPDATE log of action table  //
/////////////////////////////////
function updatelog(log) {
  var window_log = document.getElementById("window_log");

  while (window_log.firstChild) {
      window_log.removeChild(window_log.lastChild);
  }

  for (let j=0; j < log.length; j++) {
      let row = window_log.insertRow(0);
      let cell1 = row.insertCell(0);
      let cell2 = row.insertCell(1);
      cell1.innerHTML = log[j]["datetime"]
      cell2.innerHTML = log[j]["action"]
  }
}
