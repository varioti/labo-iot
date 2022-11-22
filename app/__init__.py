import pytest as pytest
from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler

from config import Config
from flask_socketio import SocketIO

app = Flask(__name__)

app.config.from_object(Config)
app.app_context().push()

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

socketio = SocketIO(app)

from app import routes
