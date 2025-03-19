from flask import render_template, redirect, url_for, flash, request, jsonify, Blueprint
from flask_login import login_user, logout_user, current_user, login_required
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import urlparse
from app import db, app
from models import User, Car, Booking
from forms import LoginForm, RegistrationForm, BookingForm, CarForm
from datetime import datetime, timedelta


@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home')


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    # Wenn die Methode GET ist → Zeige das Login-Formular an
    if request.method == "GET":
        return render_template("login.html", form=form)

    # Wenn JSON-Daten gesendet werden (API-Login)
    if request.content_type == "application/json":
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(password):
            access_token = create_access_token(identity=user.id)
            return jsonify(access_token=access_token)
        return jsonify({"msg": "Invalid credentials"}), 401

    # Wenn Formulardaten gesendet werden (Web-Login)
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Login erfolgreich!", "success")
            return redirect(url_for("index"))

    flash("Ungültige Anmeldedaten!", "danger")
    return redirect(url_for("login"))

@app.route('/logout', methods=['POST'])
@login_required  # Für Session-User
@jwt_required(optional=True)  # Falls jemand mit JWT kommt
def logout():
    if get_jwt_identity():
        return jsonify({"msg": "Logged out successfully"}), 200
    logout_user()
    flash('Du wurdest erfolgreich ausgeloggt.', 'success')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Benutzername bereits vergeben. Bitte wählen Sie einen anderen.', 'danger')
            return render_template('register.html', title='Registrierung', form=form)
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data)
        )
        db.session.add(user)
        db.session.commit()
        flash('Registrierung erfolgreich! Sie können sich jetzt anmelden.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Registrierung', form=form)

@app.route('/bookings', methods=['GET', 'POST'])
@login_required
def bookings():
    form = BookingForm()
    available_cars = Car.query.filter_by(available=True).all()
    user_bookings = Booking.query.filter_by(user_id=current_user.id).all()

    # Setze die Optionen für das Dropdown-Feld
    form.car_id.choices = [(car.id, f"{car.brand} {car.model} - {car.license_plate}") for car in available_cars]

    if request.method == "POST":
        print("🔍 POST-Request erkannt!")
        print(request.form)  # Zeigt die gesendeten Formulardaten an

    if form.validate_on_submit():
        print("✅ Form wurde validiert!")
        car_id = form.car_id.data
        start_date = form.start_date.data
        end_date = form.end_date.data
        print(f"🔍 Daten erhalten: Auto-ID={car_id}, Start={start_date}, Ende={end_date}")

        # Prüfen, ob das Auto im Zeitraum bereits gebucht ist
        existing_booking = Booking.query.filter(
            Booking.car_id == car_id,
            Booking.start_date < end_date,
            Booking.end_date > start_date
        ).first()

        if existing_booking:
            print("❌ Buchung nicht möglich: Auto bereits gebucht.")
            flash("Dieses Auto ist im gewählten Zeitraum bereits gebucht.", "danger")
        else:
            new_booking = Booking(user_id=current_user.id, car_id=car_id, start_date=start_date, end_date=end_date)
            db.session.add(new_booking)
            db.session.commit()
            print("✅ Buchung erfolgreich gespeichert!")
            flash("Buchung erfolgreich erstellt!", "success")
            return redirect(url_for('bookings'))

    # Debugging: Wenn das Formular nicht validiert wurde
    if form.errors:
        print("⚠️ Fehler bei der Validierung:", form.errors)
        flash("Es gab ein Problem mit dem Buchungsformular.", "danger")

    return render_template('bookings.html', form=form, available_cars=available_cars, user_bookings=user_bookings)


@app.route('/add_car', methods=['GET', 'POST'])
@login_required
def add_car():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    form = CarForm()
    if form.validate_on_submit():
        new_car = Car(
            model=form.model.data,
            brand=form.brand.data,
            license_plate=form.license_plate.data,
            available=True
        )
        db.session.add(new_car)
        db.session.commit()
        flash('Auto erfolgreich hinzugefügt!', 'success')
        return redirect(url_for('index'))
    
    return render_template('add_car.html', form=form)

@app.route('/check_availability', methods=['POST'])
@login_required
def check_availability():
    data = request.get_json()
    car_id = data.get('car_id')
    start_date = datetime.strptime(data.get('start_date'), "%Y-%m-%dT%H:%M")
    end_date = datetime.strptime(data.get('end_date'), "%Y-%m-%dT%H:%M")

    existing_booking = Booking.query.filter(
        Booking.car_id == car_id,
        Booking.end_date > start_date,
        Booking.start_date < end_date
    ).first()

    if existing_booking:
        return jsonify({"available": False, "message": "Dieses Auto ist im gewählten Zeitraum bereits gebucht."})
    
    return jsonify({"available": True, "message": "Dieses Auto ist verfügbar!"})

@app.route('/cancel_booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    # Überprüfen, ob der Benutzer die Buchung wirklich besitzt
    if booking.user_id != current_user.id:
        flash("Du kannst nur deine eigenen Buchungen stornieren!", "danger")
        return redirect(url_for('bookings'))

    # Auto wieder auf verfügbar setzen
    car = Car.query.get(booking.car_id)
    if car:
        car.available = True

    db.session.delete(booking)
    db.session.commit()

    flash("Die Buchung wurde erfolgreich storniert.", "success")
    return redirect(url_for('bookings'))