# config.py - Configuration PostgreSQL

import os
import secrets
from pathlib import Path
from urllib.parse import quote_plus

class Config:
    # ⚠️ En dev, le fallback ne doit PAS être aléatoire (secrets.token_hex(32))
    # car le reloader Flask (debug=True) redémarre le processus à chaque
    # modification de fichier. Une clé aléatoire à chaque démarrage invalide
    # tous les cookies de session déjà posés → erreur "CSRF session token
    # is missing" dès qu'on soumet un formulaire juste après un reload.
    # En production, définissez TOUJOURS la variable d'environnement
    # SECRET_KEY avec une vraie valeur secrète et stable.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-cle-fixe-a-ne-jamais-utiliser-en-production'
  
    BASE_DIR = Path(__file__).parent
    
    # ← POSTGRESQL (remplace SQLite)
    # En production, DATABASE_URL DOIT être défini via variable d'environnement.
    # Le fallback ci-dessous est réservé au développement local.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://mutuelle_user:mutuelle_dev_pass@localhost:5432/mutuelle_db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuration PostgreSQL optimisée
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 30,
        'pool_size': 10,
        'max_overflow': 20,
    }
    
    # Email
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'Mutuelle Solidaire <patricedetoh@upgc.edu.ci>')
    #MAIL_USERNAME=ton_email@gmail.com
    #MAIL_PASSWORD=ton_mot_de_passe_application_gmail
    #MAIL_DEFAULT_SENDER=Mutuelle Solidaire <ton_email@gmail.com>
    
    # Upload
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', str(BASE_DIR / 'static' / 'uploads'))
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    
    # Sécurité
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'false').lower() in ['true', 'on', '1']
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600
    WTF_CSRF_SSL_STRICT = os.environ.get('WTF_CSRF_SSL_STRICT', 'false').lower() in ['true', 'on', '1']

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False
    MAIL_SUPPRESS_SEND = False
    SESSION_COOKIE_SECURE = True
    WTF_CSRF_SSL_STRICT = True

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}