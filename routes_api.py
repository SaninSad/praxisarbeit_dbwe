from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from app import db
from models import Booking, Car, User
from datetime import datetime

api = Blueprint('api', __name__)

@api.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=str(user.id))
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Invalid credentials"}), 401

@api.route('/api/bookings', methods=['GET'])
@jwt_required()
def get_bookings():
    bookings = Booking.query.all()
    return jsonify([{
        'id': booking.id,
        'user_id': booking.user_id,
        'car_id': booking.car_id,
        'start_date': booking.start_date.strftime('%Y-%m-%d %H:%M'),
        'end_date': booking.end_date.strftime('%Y-%m-%d %H:%M')
    } for booking in bookings])

@api.route('/api/bookings/<int:booking_id>', methods=['GET'])
@jwt_required()
def get_booking(booking_id):
    booking = Booking.query.get(booking_id)
    if booking is None:
        return jsonify({'error': 'Buchung nicht gefunden'}), 404
    return jsonify({
        'id': booking.id,
        'user_id': booking.user_id,
        'car_id': booking.car_id,
        'start_date': booking.start_date.strftime('%Y-%m-%d %H:%M'),
        'end_date': booking.end_date.strftime('%Y-%m-%d %H:%M')
    })

@api.route('/api/bookings', methods=['POST'])
@jwt_required()
def create_booking():
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data or 'car_id' not in data or 'start_date' not in data or 'end_date' not in data:
        return jsonify({'error': 'Ungültige Daten'}), 400

    car_id = data['car_id']
    start_date = datetime.strptime(data['start_date'], '%Y-%m-%d %H:%M')
    end_date = datetime.strptime(data['end_date'], '%Y-%m-%d %H:%M')

    overlapping_booking = Booking.query.filter(
        Booking.car_id == car_id,
        Booking.end_date >= start_date,
        Booking.start_date <= end_date
    ).first()

    if overlapping_booking:
        return jsonify({'error': 'Auto ist in diesem Zeitraum bereits gebucht'}), 400

    new_booking = Booking(user_id=user_id, car_id=car_id, start_date=start_date, end_date=end_date)
    db.session.add(new_booking)
    db.session.commit()

    return jsonify({'message': 'Buchung erfolgreich', 'booking_id': new_booking.id}), 201

@api.route('/api/bookings/<int:booking_id>', methods=["DELETE"])
@jwt_required()
def delete_booking(booking_id):
    try:
        current_user_id = int(get_jwt_identity())  # Token-ID in Integer umwandeln

        booking = Booking.query.get(booking_id)  # Buchung suchen

        if not booking:
            return jsonify({"error": "Buchung nicht gefunden"}), 404

        if booking.user_id != current_user_id:
            return jsonify({"error": "Keine Berechtigung"}), 403

        db.session.delete(booking)
        db.session.commit()

        return jsonify({"message": "Buchung erfolgreich storniert"}), 200

    except Exception as e:
        return jsonify({"error": f"Interner Fehler: {str(e)}"}), 500


