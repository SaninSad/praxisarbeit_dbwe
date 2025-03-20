from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from app import db # Datenbank-Instanz importieren
from models import Booking, Car, User # Import der Datenbank-Modelle
from datetime import datetime  # Datumsformatierung für Buchungen

# API Blueprint für getrennte API-Routen
api = Blueprint('api', __name__)

# API-Login-Route (Benutzer kann sich authentifizieren und erhält ein JWT-Token)
@api.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json() # JSON-Daten aus der Anfrage abrufen
    username = data.get("username")
    password = data.get("password")

    # Benutzer in der Datenbank suchen
    user = User.query.filter_by(username=username).first()

    # Überprüfung der Anmeldedaten
    if user and user.check_password(password):
        access_token = create_access_token(identity=str(user.id)) # JWT-Token erstellen
        return jsonify(access_token=access_token), 200 # Token zurückgeben
    else:
        return jsonify({"msg": "Invalid credentials"}), 401  # Fehler bei falschen Daten

# API-Route: Alle Buchungen abrufen (nur für authentifizierte Benutzer)
@api.route('/api/bookings', methods=['GET'])
@jwt_required() # Authentifizierung über JWT erforderlich
def get_bookings():
    bookings = Booking.query.all() # Alle Buchungen aus der Datenbank abrufen
    return jsonify([{
        'id': booking.id,
        'user_id': booking.user_id,
        'car_id': booking.car_id,
        'start_date': booking.start_date.strftime('%Y-%m-%d %H:%M'),
        'end_date': booking.end_date.strftime('%Y-%m-%d %H:%M')
    } for booking in bookings]) # JSON-Antwort mit allen Buchungen

# API-Route: Einzelne Buchung abrufen
@api.route('/api/bookings/<int:booking_id>', methods=['GET'])
@jwt_required() # Authentifizierung über JWT erforderlich
def get_booking(booking_id):
    booking = Booking.query.get(booking_id) # Buchung in der Datenbank suchen
    if booking is None:
        return jsonify({'error': 'Buchung nicht gefunden'}), 404 # Falls nicht vorhanden, Fehler zurückgeben
    return jsonify({
        'id': booking.id,
        'user_id': booking.user_id,
        'car_id': booking.car_id,
        'start_date': booking.start_date.strftime('%Y-%m-%d %H:%M'),
        'end_date': booking.end_date.strftime('%Y-%m-%d %H:%M')
    })     # JSON-Antwort mit Buchungsdetails

# API-Route: Neue Buchung erstellen
@api.route('/api/bookings', methods=['POST'])
@jwt_required() # Authentifizierung erforderlich
def create_booking():
    user_id = get_jwt_identity() # Benutzer-ID aus dem Token abrufen
    data = request.get_json() # JSON-Daten aus der Anfrage abrufen

    # Überprüfung, ob alle benötigten Daten vorhanden sind
    if not data or 'car_id' not in data or 'start_date' not in data or 'end_date' not in data:
        return jsonify({'error': 'Ungültige Daten'}), 400

    car_id = data['car_id']
    start_date = datetime.strptime(data['start_date'], '%Y-%m-%d %H:%M')    # Datum in datetime-Objekt umwandeln
    end_date = datetime.strptime(data['end_date'], '%Y-%m-%d %H:%M')

    # Prüfen, ob das Auto im gewählten Zeitraum bereits gebucht wurde
    overlapping_booking = Booking.query.filter(
        Booking.car_id == car_id,
        Booking.end_date >= start_date,
        Booking.start_date <= end_date
    ).first()

    if overlapping_booking:
        return jsonify({'error': 'Auto ist in diesem Zeitraum bereits gebucht'}), 400
   
    # Neue Buchung anlegen und speichern
    new_booking = Booking(user_id=user_id, car_id=car_id, start_date=start_date, end_date=end_date)
    db.session.add(new_booking)
    db.session.commit()

    return jsonify({'message': 'Buchung erfolgreich', 'booking_id': new_booking.id}), 201

# API-Route: Buchung löschen
@api.route('/api/bookings/<int:booking_id>', methods=["DELETE"])
@jwt_required() # Authentifizierung erforderlich
def delete_booking(booking_id):
    try:
        current_user_id = int(get_jwt_identity())  # Token-ID in Integer umwandeln

        booking = Booking.query.get(booking_id)  # Buchung suchen

        if not booking:
            return jsonify({"error": "Buchung nicht gefunden"}), 404 # Falls nicht gefunden, Fehler zurückgeben

        if booking.user_id != current_user_id:
            return jsonify({"error": "Keine Berechtigung"}), 403 # Falls nicht der Besitzer, Zugriff verweigern

        db.session.delete(booking)
        db.session.commit()

        return jsonify({"message": "Buchung erfolgreich storniert"}), 200 # Erfolgreiche Stornierung zurückgeben

    except Exception as e:
        return jsonify({"error": f"Interner Fehler: {str(e)}"}), 500 # Fehler zurückgeben, falls unerwartet


