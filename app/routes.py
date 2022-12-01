from datetime import datetime
from flask import render_template, redirect, Flask
from flask import url_for, request
import time 

from app import app, db, scheduler, socketio
from app.models import Devices, MeasureConsumption, AdvicesConsumption, WindowLog
from sensors.window.Window import Window
from sensors.energy.energy import Energy

import pandas as pd
import json
import plotly
import plotly.express as px

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
    e[device.name] = Energy(hub_port= device.hub_port,nb_volt= device.nb_volt, simulate=True) # Set simulate to True if phidgets not plugged

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
    socketio.emit("update", (is_open, temp_in, temp_out, hum, current_state, mode))
    socketio.emit("updatelog", (log))

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
            device = Devices.query.filter(Devices.name == eid).first()
            MeasureConsumption.add_new_measure(sensor.get_watt(), device.id)
            devices.append(device)

        now = datetime.today()
        begin_day = datetime(now.year, now.month, now.day)
        nb_hours = (now - begin_day).total_seconds()/3600
        
        today_conso = 0 
        for device in devices:
            devices_names.append(device.name)
            # Get total kWh of the device from today 0:00 to now
            device_today_measure = device.get_between_measures(begin_day, now)
            nb_hours = (device_today_measure[-1].datetime - device_today_measure[0].datetime).total_seconds()/3600 #nb hours between first measure of the day and last
            device_conso = ((sum(m.measure for m in (device_today_measure)) / len(device_today_measure))/100) * nb_hours
            today_conso += device_conso

            # Get all measures from device
            devices_measures.append(list(map(lambda x: x.get_serializable_measure(), list(device.measures))))
    
    # Send info to page
    socketio.emit("newmeasure", (devices_names, devices_measures))
    socketio.emit("newdashboard", (current_total, round(today_conso, 2)))
    

# Set the reccurent backround action (for window) each 5 sec
scheduler.add_job(id='window', func=window_behaviour, trigger="interval", seconds=5)

# Set the reccurent backround action (for energy) each 5 sec
scheduler.add_job(id='energy', func=energy_behaviour, trigger="interval", seconds=5)

######################################################################################
# ROUTES #
##########

### MAIN PAGE ###
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

    devices_conso={}
    for key in e.keys():
        e[key].make_measure()
        devices_conso[key] = e[key].get_watt()

    return render_template("dashboard.html", temp_in=temp_in, temp_out=temp_out, temp_desired=w.temp_desired, hum=hum, state=current_state, is_open=is_open, mode_auto=mode, 
                                             energy=energy, devices_conso=devices_conso)

### WINDOW PAGES ###
# Open window input
@app.route("/open/")
def manual_open():
    w.open()
    w.set_manual()
    return redirect(url_for("dashboard "))

# Close window input
@app.route("/close/")
def manual_close():
    w.close()
    w.set_manual()
    return redirect(url_for("dashboard"))

# Change mode (auto or manual) of the window input
@app.route("/mode/")
def set_mode():
    if w.mode_auto :
        w.set_manual()
    else :
        w.set_auto()
    return redirect(url_for("dashboard"))

# Log of auto actions of the window page
@app.route("/window/")
def window():
    with app.app_context():
        log = list(map(lambda x: x.get_serializable_action(), list(WindowLog.query.all())))

    return render_template("window/log.html", log=log)

# Update window informations page
@app.route("/update/")
def update():
    return render_template("window/parameters.html", temp=w.temp_desired, max_hum=w.max_hum)

# Update temperature desired input
@app.route("/update/temperature/")
def update_temp():
    if request.args.get("temp", None):
        try:
            w.set_temp_desired(float(request.args["temp"]))
        except:
            pass

    return redirect(url_for("dashboard"))

# Update max humidity desired input
@app.route("/update/humidity/")
def update_hum():
    if request.args.get("hum", None):
        try:
            w.set_max_hum(float(request.args["hum"]))
        except:
            pass

    return redirect(url_for("dashboard"))

### CONSO PAGES ###
# Tables of each mesures per device page
@app.route("/energy_history/")
def histo_conso():
    return render_template("histo_conso.html")

# Informations about light page
@app.route("/light/")
def light_advice():

    light_advices = AdvicesConsumption.query.filter(AdvicesConsumption.type_d.endswith(" Ampoule")).all()

    light = Devices.query.filter(Devices.name == "Lampe").first()
    df = pd.DataFrame({
            "Temps": [x.datetime for x in light.measures],
            "Puissance": [x.measure for x in light.measures],
        })
    fig = px.line(df, x="Temps", y="Puissance")
    fig.update_traces(showlegend=True)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    header="Puissance utilisée par la Lampe"
    description = """Puissance utilisée par la Lampe en fonction du temps."""

    return render_template("devices/advice.html", consumption=[], advices=light_advices, gen_advices=[],
                                                         graphJSON=graphJSON, header=header,description=description)

# Informations about fridge page
@app.route("/fridge/")
def fridge_advice():
    gen_advices =  AdvicesConsumption.query.filter(AdvicesConsumption.type_d.endswith("Achat G")).all()
    fridge_consumption = AdvicesConsumption.query.filter(AdvicesConsumption.device.endswith("Frigo")).all()
    fridge_advices = AdvicesConsumption.query.filter(AdvicesConsumption.device.endswith("Frigidaire")).all()

    fridge = Devices.query.filter(Devices.name == "Frigo").first()
    df = pd.DataFrame({
            "Temps": [x.datetime for x in fridge.measures],
            "Puissance": [x.measure for x in fridge.measures],
        })
    fig = px.line(df, x="Temps", y="Puissance")
    fig.update_traces(showlegend=True)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    header="Puissance utilisée par le Frigo"
    description = """Puissance utilisée par le Frigo en fonction du temps."""


    return render_template("devices/advice.html", consumption=fridge_consumption, advices=fridge_advices, gen_advices=gen_advices,
                                                         graphJSON=graphJSON, header=header,description=description)

# Informations about dishwasher page
@app.route("/dishwasher/")
def dishwasher_advice():

    gen_advices =  AdvicesConsumption.query.filter(AdvicesConsumption.device.endswith("Achat")).all()
    dishwasher_advices = AdvicesConsumption.query.filter(AdvicesConsumption.device.endswith("Lave-vaisselle")).all()

    dishwasher = Devices.query.filter(Devices.name == "Lave-vaisselle").first()
    df = pd.DataFrame({
            "Temps": [x.datetime for x in dishwasher.measures],
            "Puissance": [x.measure for x in dishwasher.measures],
        })
    fig = px.line(df, x="Temps", y="Puissance")
    fig.update_traces(showlegend=True)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    header="Puissance utilisée par le Lave-vaisselle"
    description = """Puissance utilisée par le Frigo en fonction du temps."""


    return render_template("devices/advice.html", consumption=[], advices=dishwasher_advices, gen_advices=gen_advices,
                                                         graphJSON=graphJSON, header=header,description=description)

# Informations about hob page
@app.route("/hob/")
def hob_advice():

    hob = Devices.query.filter(Devices.name == "Taque de cuisson").first()
    df = pd.DataFrame({
            "Temps": [x.datetime for x in hob.measures],
            "Puissance": [x.measure for x in hob.measures],
        })
    fig = px.line(df, x="Temps", y="Puissance")
    fig.update_traces(showlegend=True)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    header="Puissance utilisée par la Taque de cuisson"
    description = """Puissance utilisée par la Taque de cuisson en fonction du temps."""


    return render_template("devices/advice.html", consumption=[], advices=[], gen_advices=[],
                                                         graphJSON=graphJSON, header=header,description=description)

# Informations about boiler page
@app.route("/boil/")
def boiler_advice():

    boiler = Devices.query.filter(Devices.name == "Bouilloire").first()
    df = pd.DataFrame({
            "Temps": [x.datetime for x in boiler.measures],
            "Puissance": [x.measure for x in boiler.measures],
        })
    fig = px.line(df, x="Temps", y="Puissance")
    fig.update_traces(showlegend=True)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    header="Puissance utilisée par la Bouilloire"
    description = """Puissance utilisée par la Bouilloire."""


    return render_template("devices/advice.html", consumption=[], advices=[], gen_advices=[],
                                                         graphJSON=graphJSON, header=header,description=description)


#######
# RUN #
#######

if __name__ == "__main__":
    socketio.run(app)