from datetime import datetime
from flask import render_template, redirect, Flask
from flask import url_for, request
import time 

from app import app, db, scheduler, socketio
from app.models import Devices, MeasureConsumption, AdvicesConsumption, WindowLog
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
    action = w.behavior()
    if action is not None :
        WindowLog.add_new_action(action)
    with scheduler.app.app_context():
        log = list(map(lambda x: x.get_serializable_action(), list(WindowLog.query.all())))
    temp_in, temp_out, hum = w.get_measures()
    current_state = w.repr_state()
    is_open = w.get_is_open()
    mode = w.mode_auto

    # Send info to page
    socketio.emit("update", (is_open, temp_in, temp_out, hum, current_state, mode, log))

# Recurrent background action of window
def energy_behaviour():
    devices = []
    devices_names = []
    devices_measures = []

    current_total = 0
    with scheduler.app.app_context():
        for eid in e.keys():
            sensor = e[eid]
            sensor.make_measure()
            current_total += sensor.get_watt()/100
            MeasureConsumption.add_new_measure(sensor.get_watt(), eid)
            devices.append(Devices.query.get(eid))

        now = datetime.today()
        begin_day = datetime(now.year, now.month, now.day)
        nb_hours = (now - begin_day).total_seconds()/3600
        
        today_conso = 0 
        for device in devices:
            devices_names.append(device.name)
            # Get total kWh of the device from today 0:00 to now
            device_today_measure = device.get_between_measures(begin_day, now)
            device_conso = ((sum(m.measure for m in (device_today_measure)) / len(device_today_measure))/100) * nb_hours
            today_conso += device_conso
            print(today_conso)

            # Get all measures from device
            devices_measures.append(list(map(lambda x: x.get_serializable_measure(), list(device.measures))))
    print(today_conso)
    # Send info to page
    socketio.emit("newmeasure", (devices_names, devices_measures))
    socketio.emit("newdashboard", (current_total, round(today_conso, 2)))
    

# Set the reccurent backround action (for window) each 5 sec
scheduler.add_job(id='window', func=window_behaviour, trigger="interval", seconds=5)

# Set the reccurent backround action (for energy) each 5 sec
scheduler.add_job(id='energy', func=energy_behaviour, trigger="interval", seconds=5)

##########
# ROUTES #
##########

@app.route("/")
def dashboard():
    temp_in, temp_out, hum = w.get_measures()
    current_state = w.repr_state()
    is_open = w.get_is_open()
    mode = w.mode_auto

    # Static values
    energy={
        "nb_app":5,
        "kw_actual":0.5,
        "kwh_today":40,
        "pc_today":4.5,
        "kwh_week":40,
        "pc_week":-2,
        "kwh_month":40,
        "pc_month":5
    }

    return render_template("dashboard.html", temp_in=temp_in, temp_out=temp_out, hum=hum, state=current_state, is_open=is_open, mode_auto=mode, energy=energy)


@app.route("/window/")
def window(state=False):
    temp_in, temp_out, hum = w.get_measures()
    current_state = w.repr_state()
    is_open = w.get_is_open()
    mode = w.mode_auto

    with app.app_context():
        log = list(map(lambda x: x.get_serializable_action(), list(WindowLog.query.all())))

    return render_template("windows.html", temp_in=temp_in, temp_out=temp_out, hum=hum, state=current_state, is_open=is_open, mode_auto=mode, log=log)

@app.route("/open/")
def manual_open():
    w.open()
    w.set_manual()
    return redirect(url_for("dashboard "))

@app.route("/close/")
def manual_close():
    w.close()
    w.set_manual()
    return redirect(url_for("dashboard"))

@app.route("/mode/")
def set_mode():
    if w.mode_auto :
        w.set_manual()
    else :
        w.set_auto()

    return redirect(url_for("dashboard"))

@app.route("/energy_history/")
def histo_conso():
    return render_template("histo_conso.html")


@app.route("/light/")
def light_advice():

    light_advices = AdvicesConsumption.query.filter(AdvicesConsumption.type_d.endswith(" Ampoule")).all()
    return render_template("light.html", light_advices=light_advices)

@app.route("/fridge/")
def fridge_advice():

    gen_advices =  AdvicesConsumption.query.filter(AdvicesConsumption.type_d.endswith("Achat G")).all()
    fridge_consumption = AdvicesConsumption.query.filter(AdvicesConsumption.device.endswith("Frigo")).all()
    fridge_advices = AdvicesConsumption.query.filter(AdvicesConsumption.device.endswith("Frigidaire")).all()

    return render_template("fridge.html", fridge_consumption=fridge_consumption, fridge_advices=fridge_advices,
                            gen_advices=gen_advices)

@app.route("/dishwasher/")
def dishwasher_advice():

    gen_advices =  AdvicesConsumption.query.filter(AdvicesConsumption.device.endswith("Achat")).all()
    dishwasher_advices = AdvicesConsumption.query.filter(AdvicesConsumption.device.endswith("Lave-vaisselle")).all()

    return render_template("dishwasher.html", dishwasher_advices=dishwasher_advices, gen_advices=gen_advices)


#######
# RUN #
#######

if __name__ == "__main__":
    socketio.run(app)