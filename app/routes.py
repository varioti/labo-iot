from flask import render_template, redirect, Flask
from flask import url_for, request
import time 

from app import app, db, scheduler, socketio
from sensors.window.Window import Window

from app import db

##########
# WINDOW #
##########

w = Window(is_testing=True) # Set is_testing to True if phidgets not plugged

# Recurrent background action of window
def window_behaviour():
    w.behavior()
    temp_in, temp_out, hum = w.get_measures()
    current_state = w.repr_state()
    is_open = w.get_is_open()

    # Send info to page
    socketio.emit("update", (is_open, temp_in, temp_out, hum, current_state))

# Set the reccurent backround action (for window) each 5 sec
scheduler.add_job(id='window', func=window_behaviour, trigger="interval", seconds=5)

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


#######
# RUN #
#######

if __name__ == "__main__":
    socketio.run(app)