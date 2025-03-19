from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from flask_jwt_extended import JWTManager


app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

app.config['JWT_SECRET_KEY'] = 'dein_geheimer_schlüssel'
jwt = JWTManager(app)  # ✅ JWT Manager Initialisieren

from routes import *
from routes_api import api
app.register_blueprint(api)

