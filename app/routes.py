from datetime import datetime, timedelta
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
    if device.hub_port == -1:
        e[device.name] = Energy(hub_port= 0,nb_volt= device.nb_volt, simulate=True) # Set simulate to True if phidgets not plugged
    else:
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
            current_total += sensor.get_watt()/1000
            device = Devices.query.filter(Devices.name == eid).first()
            MeasureConsumption.add_new_measure(sensor.get_watt(), device.id)
            devices.append(device)

        now = datetime.today()
        begin_day = datetime(now.year, now.month, now.day)
        monday = now - timedelta(days=now.weekday())
        begin_week = datetime(monday.year, monday.month, monday.day)
        begin_month = datetime(now.year, now.month, 1)

        nb_hours = (now - begin_day).total_seconds()/3600
        
        devices_actual_conso={}
        devices_summary_conso={}

        today_conso = 0 
        week_conso = 0
        month_conso = 0
        for device in devices:
            devices_names.append(device.name)

            # Get total kWh of the device from today 0:00 to now
            device_today_measure = device.get_between_measures(begin_day, now)
            nb_hours = (device_today_measure[-1].datetime - device_today_measure[0].datetime).total_seconds()/3600 #nb hours between first measure of the day and last
            today_device_conso = ((sum(m.measure for m in (device_today_measure)) / len(device_today_measure))) * nb_hours
            today_conso += today_device_conso/1000

            # Get total kWh of the device from beginning of the week to now
            device_week_measure = device.get_between_measures(begin_week, now)
            nb_hours = (device_week_measure[-1].datetime - device_week_measure[0].datetime).total_seconds()/3600 #nb hours between first measure of the week and last
            week_device_conso = ((sum(m.measure for m in (device_week_measure)) / len(device_week_measure))) * nb_hours
            week_conso += week_device_conso/1000

            # Get total kWh of the device from beginning ot the month to now
            device_month_measure = device.get_between_measures(begin_month, now)
            nb_hours = (device_month_measure[-1].datetime - device_month_measure[0].datetime).total_seconds()/3600 #nb hours between first measure of the day and last
            month_device_conso = ((sum(m.measure for m in (device_month_measure)) / len(device_month_measure))) * nb_hours
            month_conso += month_device_conso/1000

            devices_summary_conso[device.name] = {"today":round(today_device_conso/1000,3),"week":round(week_device_conso/1000,3),"month":round(month_device_conso/1000,3)}

            # Get all measures from device
            devices_measures.append(list(map(lambda x: x.get_serializable_measure(), list(device.measures))))

            devices_actual_conso[device.name] = round(e[device.name].get_watt(),1)
    
    # Send info to page
    socketio.emit("newdashboard", (round(current_total,2), round(today_conso, 3), round(week_conso, 3), round(month_conso, 3), devices_actual_conso))

    # Send info to devices pages
    socketio.emit("updatedevices", (devices_summary_conso, devices_actual_conso))
    

# Set the reccurent backround action (for window) each 5 sec
scheduler.add_job(id='window', func=window_behaviour, trigger="interval", seconds=5)

# Set the reccurent backround action (for energy) each 5 sec
scheduler.add_job(id='energy', func=energy_behaviour, trigger="interval", seconds=2)

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

    # Static values waiting first update from sheduled task each 2 sec
    energy={
        "nb_app":5,
        "kw_actual":0,
        "kwh_today":0,
        "pc_today":0,
        "kwh_week":0,
        "pc_week":0,
        "kwh_month":0,
        "pc_month":0
    }

    devices_conso={}
    for key in e.keys():
        e[key].make_measure()
        devices_conso[key] = round(e[key].get_watt(),1)

    return render_template("dashboard.html", temp_in=temp_in, temp_out=temp_out, temp_desired=w.temp_desired, hum=hum, state=current_state, is_open=is_open, mode_auto=mode, 
                                             energy=energy, devices_conso=devices_conso)

### WINDOW PAGES ###
# Open window input
@app.route("/open/")
def manual_open():
    w.open()
    w.set_manual()
    return redirect(url_for("dashboard"))

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

    # Advices
    light_advices = AdvicesConsumption.query.filter(AdvicesConsumption.type_d.endswith(" Ampoule")).all()

    # Graph
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

    # Compute the mean power of light (when power on) to add it in the conso advices
    measures_light_on = [x.measure for x in light.measures if x.measure > 0.5]
    mean_power = round(sum(measures_light_on)/len(measures_light_on),1)
    light_advices.append({"advice":f"Votre ampoule utilise {mean_power} W en moyenne quand elle est allumée."})


    return render_template("devices/advice.html", consumption=light_advices, advices=[], gen_advices=[], device_name="Lampe",
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


    return render_template("devices/advice.html", consumption=fridge_consumption, advices=fridge_advices, gen_advices=gen_advices, device_name="Frigo",
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


    return render_template("devices/advice.html", consumption=[], advices=dishwasher_advices, gen_advices=gen_advices, device_name="Lave-vaisselle",
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


    return render_template("devices/advice.html", consumption=[], advices=[], gen_advices=[], device_name="Taque de cuisson",
                                                         graphJSON=graphJSON, header=header,description=description)

# Informations about boiler page
@app.route("/boil/")
def boiler_advice():

    boiler = Devices.query.filter(Devices.name == "Bouilloire").first()
    consumption = AdvicesConsumption.query.filter(AdvicesConsumption.type_d.endswith(" Bouilloire")).all()

    df = pd.DataFrame({
            "Temps": [x.datetime for x in boiler.measures],
            "Puissance": [x.measure for x in boiler.measures],
        })
    fig = px.line(df, x="Temps", y="Puissance")
    fig.update_traces(showlegend=True)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    header="Puissance utilisée par la Bouilloire"
    description = """Puissance utilisée par la Bouilloire."""


    return render_template("devices/advice.html", consumption=consumption, advices=[], gen_advices=[], device_name="Bouilloire",
                                                         graphJSON=graphJSON, header=header,description=description)


#######
# RUN #
#######

if __name__ == "__main__":
    socketio.run(app)