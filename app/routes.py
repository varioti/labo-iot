from flask import render_template, redirect, Flask
from flask import url_for, request
import time 

from app import app, db, scheduler, socketio
from app.models import Devices, MeasureConsumption
from sensors.window.Window import Window
from sensors.energy.energy import Energy

from app import db

###########
# SENSORS #
###########

w = Window(is_testing=True) # Set is_testing to True if phidgets not plugged

devices = Devices.query.all()
e = {}
for device in devices:
    e[device.id] = Energy(hub_port= device.hub_port,nb_volt= device.nb_volt, simulate=True) # Set simulate to True if phidgets not plugged

# Recurrent background action of window
def window_behaviour():
    w.behavior()
    temp_in, temp_out, hum = w.get_measures()
    current_state = w.repr_state()
    is_open = w.get_is_open()

    # Send info to page
    socketio.emit("update", (is_open, temp_in, temp_out, hum, current_state))

# Recurrent background action of window
def energy_behaviour():
    devices_names = []
    devices_measures = []

    for eid in e.keys():
        sensor = e[eid]
        sensor.make_measure()
        MeasureConsumption.add_new_measure(sensor.get_watt(), eid)
        devices_names.append(Devices.query.get(eid).name)
        devices_measures.append(MeasureConsumption.query.filter(MeasureConsumption.device_id == eid))

    # Send info to page
    socketio.emit("newmeasure", (devices_names, devices_measures))
    

# Set the reccurent backround action (for window) each 5 sec
scheduler.add_job(id='window', func=window_behaviour, trigger="interval", seconds=5)

# Set the reccurent backround action (for energy) each 5 sec
scheduler.add_job(id='energy', func=energy_behaviour, trigger="interval", seconds=5)

##########
# ROUTES #
##########

@app.route("/")
def hello_world():
    return render_template("index.html")


@app.route("/window/", methods=["GET", "POST"])
def window(state=False):
    state_window = state
    if request.method == 'POST':
        return redirect(url_for("window"))

    return render_template("windows.html", state_window=state_window)

@app.route("/open/")
def manual_open():
    w.open()
    return redirect(url_for("window"))

@app.route("/close/")
def manual_close():
    w.close()
    return redirect(url_for("window"))

@app.route("/energy_history/")
def histo_conso():
    return render_template("histo_conso.html")



#######
# RUN #
#######

if __name__ == "__main__":
    socketio.run(app)