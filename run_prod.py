# run_prod.py - Version Production (CORRIGÉE)

import os
from waitress import serve
from dotenv import load_dotenv
from app import app, db, init_db
import logging
from datetime import datetime

# Charger les variables d'environnement
load_dotenv()

# Configuration des logs
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/mutuelle_{datetime.now().strftime("%Y%m%d")}.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    # Créer les dossiers nécessaires
    os.makedirs('instance', exist_ok=True)
    os.makedirs('static/uploads/photos', exist_ok=True)
    os.makedirs('static/uploads/recus', exist_ok=True)
    
    # Initialiser la base de données
    with app.app_context():
        db.create_all()
        init_db()
    
    # Configuration Waitress (PARAMÈTRES VALIDES)
    host = os.environ.get('WAITRESS_HOST', '0.0.0.0')
    port = int(os.environ.get('WAITRESS_PORT', 8000))
    threads = int(os.environ.get('WAITRESS_THREADS', 4))
    connection_limit = int(os.environ.get('WAITRESS_CONNECTIONS', 100))
    
    logger.info("=" * 60)
    logger.info("🚀 MUTUELLE SOLIDAIRE - PRODUCTION")
    logger.info("=" * 60)
    logger.info(f"📁 Dossier: {os.path.abspath('.')}")
    logger.info(f"🌐 URL: http://{host}:{port}")
    logger.info(f"🧵 Threads: {threads}")
    logger.info(f"🔗 Connections: {connection_limit}")
    logger.info("=" * 60)
    
    # Démarrer le serveur avec paramètres VALIDES pour Waitress
    serve(
        app,
        host=host,
        port=port,
        threads=threads,
        connection_limit=connection_limit,  # ← Nom correct (pas 'connections')
        channel_timeout=120  # ← Timeout unique (pas recv_timeout/send_timeout)
    )