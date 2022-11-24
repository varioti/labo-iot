import pytest as pytest
from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler

from config import Config
from flask_socketio import SocketIO

app = Flask(__name__)

app.config.from_object(Config)

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

socketio = SocketIO(app)

from app import routes
