from flask import render_template, redirect, Flask
from flask import url_for, request
import time 

from app import app, db, scheduler, socketio
from app.models import Devices, MeasureConsumption, AdvicesConsumption
from sensors.window.Window import Window
from sensors.energy.energy import Energy

from app import db

###########
# SENSORS #
###########

w = Window(is_testing=True) # Set is_testing to True if phidgets not plugged
# Initializing the database
with app.app_context():
    devices =  list(Devices.query.all())
with scheduler.app.app_context():
    db.session.query(MeasureConsumption).delete()
    db.session.commit()

print(devices)

e = {}
for device in devices:
    e[device.id] = Energy(hub_port= device.hub_port,nb_volt= device.nb_volt, simulate=True) # Set simulate to True if phidgets not plugged

# Recurrent background action of window
def window_behaviour():
    w.behavior()
    temp_in, temp_out, hum = w.get_measures()
    current_state = w.repr_state()
    is_open = w.get_is_open()
    mode = w.mode_auto

    # Send info to page
    socketio.emit("update", (is_open, temp_in, temp_out, hum, current_state, mode))

# Recurrent background action of window
def energy_behaviour():
    devices_names = []
    devices_measures = []

    for eid in e.keys():
        sensor = e[eid]
        sensor.make_measure()
        MeasureConsumption.add_new_measure(sensor.get_amp(), eid)
        with scheduler.app.app_context():
            devices_names.append(Devices.query.get(eid).name)
            device_measures = list(MeasureConsumption.query.filter(MeasureConsumption.device_id == eid))
            devices_measures.append(list(map(lambda x: x.get_serializable_measure(), device_measures)))

    print(devices_names)
    print(devices_measures)

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


@app.route("/window/")
def window(state=False):
    temp_in, temp_out, hum = w.get_measures()
    current_state = w.repr_state()
    is_open = w.get_is_open()
    mode = w.mode_auto

    return render_template("windows.html", temp_in=temp_in, temp_out=temp_out, hum=hum, state=current_state, is_open=is_open, mode_auto=mode)

@app.route("/open/")
def manual_open():
    w.open()
    w.set_manual()
    return redirect(url_for("window"))

@app.route("/close/")
def manual_close():
    w.close()
    w.set_manual()
    return redirect(url_for("window"))

@app.route("/mode/")
def set_mode():
    if w.mode_auto :
        w.set_manual()
    else :
        w.set_auto()

    return redirect(url_for("window"))

@app.route("/energy_history/")
def histo_conso():
    return render_template("histo_conso.html")



#######
# RUN #
#######

if __name__ == "__main__":
    socketio.run(app)