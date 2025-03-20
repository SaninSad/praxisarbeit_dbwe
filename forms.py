# Import der FlaskForm-Klasse und der Formularfelder aus WTForms
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, DateField, DateTimeField, DateTimeLocalField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from models import User, Car  # Import der User- und Car-Modelle für Validierungszwecke

# Formular für den Login-Prozess
class LoginForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    remember_me = BooleanField('Angemeldet bleiben')
    submit = SubmitField('Login')

# Formular für die Benutzerregistrierung
class RegistrationForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    email = StringField('E-Mail', validators=[DataRequired(), Email()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    password2 = PasswordField('Passwort wiederholen', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrieren')
    
    # Prüft, ob der Benutzername bereits existiert
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Dieser Benutzername ist bereits vergeben.')

    # Prüft, ob die E-Mail bereits registriert wurde
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Diese E-Mail ist bereits registriert.')

# Formular für die Fahrzeugbuchung
class BookingForm(FlaskForm):
    car_id = SelectField('Auto', coerce=int, validators=[DataRequired()])
    start_date = DateTimeLocalField('Startdatum', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    end_date = DateTimeLocalField('Enddatum', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    submit = SubmitField('Buchen')

# Formular für das Hinzufügen eines neuen Fahrzeugs
class CarForm(FlaskForm):
    model = StringField('Modell', validators=[DataRequired()])
    brand = StringField('Marke', validators=[DataRequired()])
    license_plate = StringField('Kennzeichen', validators=[DataRequired()])
    submit = SubmitField('Auto hinzufügen')
