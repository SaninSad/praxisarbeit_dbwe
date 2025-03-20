# Import der benötigten Flask-Module
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from flask_jwt_extended import JWTManager

# Flask-Anwendung initialisieren
app = Flask(__name__)
# Konfiguration aus der Config-Klasse laden
app.config.from_object(Config)

# Initialisierung der Datenbank und Migration
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# Flask-Login initialisieren
login = LoginManager(app)
login.login_view = 'login'

# Konfiguration des JWT-Authentifizierungssystems
app.config['JWT_SECRET_KEY'] = 'dein_geheimer_schlüssel'
jwt = JWTManager(app)  # ✅ JWT Manager Initialisieren

# Import der Routen für die Web-Oberfläche und API
from routes import *
from routes_api import api

# Registrierung des API-Blueprints in der Flask-App
app.register_blueprint(api)

