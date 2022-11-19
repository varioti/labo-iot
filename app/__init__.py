import pytest as pytest
from flask import Flask

from config import Config

app = Flask(__name__)

app.config.from_object(Config)

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

from app import routes
