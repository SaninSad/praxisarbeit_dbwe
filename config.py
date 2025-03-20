# Import der notwendigen Modul
from dotenv import load_dotenv
import os

# Laden der Umgebungsvariablen aus der .env-Datei
load_dotenv()
# Basisverzeichnis der Anwendung bestimmen
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key')  
