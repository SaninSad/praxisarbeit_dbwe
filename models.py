# Import relevanter Module für Datums- und Benutzerverwaltung
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login # Import der Datenbank (SQLAlchemy) und der Login-Verwaltung

# Benutzer-Modell für die User-Authentifizierung und Verwaltung
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # Eindeutige ID für jeden Benutzer
    username = db.Column(db.String(64), index=True, unique=True) # Benutzername (muss eindeutig sein)
    email = db.Column(db.String(120), index=True, unique=True) # Eindeutige E-Mail-Adresse
    password_hash = db.Column(db.String(255), nullable=False) # Gespeichertes gehashtes Passwort

    # Beziehung zu den Buchungen (1 User kann mehrere Buchungen haben)
    bookings = db.relationship('Booking', backref='user', lazy=True)

    # Methode zum Setzen des Passworts (Hashing für Sicherheit)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Methode zum Überprüfen des Passworts
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Ladefunktion für Flask-Login (findet Benutzer anhand der ID)
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# Fahrzeug-Modell für die Verwaltung von Autos
class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True) # Eindeutige ID für jedes Fahrzeug
    model = db.Column(db.String(100))  # Fahrzeugmodell
    brand = db.Column(db.String(100)) # Automarke
    license_plate = db.Column(db.String(20), unique=True, nullable=False)  # Eindeutiges Kennzeichen (Pflichtfeld)
    available = db.Column(db.Boolean, default=True) # Verfügbarkeitsstatus des Fahrzeugs

# Buchungs-Modell für das Reservierungssystem
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Eindeutige Buchungs-ID
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # Verknüpfung zur User-Tabelle (FK)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)  # Verknüpfung zur Car-Tabelle (FK)
    start_date = db.Column(db.DateTime, nullable=False) # Startzeitpunkt der Buchung
    end_date = db.Column(db.DateTime, nullable=False) # Endzeitpunkt der Buchung
    car = db.relationship('Car', backref='bookings')  # Beziehung zu Car (1 Buchung bezieht sich auf genau 1 Auto)
