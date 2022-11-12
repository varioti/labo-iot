from flask import render_template, redirect
from flask import url_for, request

from app import app


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

    return render_template("window.html", state_window=state_window)


#######
# RUN #
#######
if __name__ == "__main__":
    app.run()
