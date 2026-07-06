# utils/tasks.py
from datetime import datetime, timedelta
from models import Membre, Cotisation
from utils.notifications import send_cotisation_reminder
from app import app, db

def send_cotisation_reminders():
    """
    Envoie des rappels de cotisations aux membres en retard
    À exécuter quotidiennement (via cron ou Task Scheduler)
    """
    with app.app_context():
        today = datetime.now()
        echeance = today + timedelta(days=7)  # Rappel 7 jours avant
        
        # Trouver les membres actifs sans cotisation du mois
        membres_actifs = Membre.query.filter_by(statut='Actif').all()
        rappel_envoye = 0
        
        for membre in membres_actifs:
            # Vérifier si cotisation du mois existe
            cotisation_mois = Cotisation.query.filter(
                Cotisation.membre_id == membre.id,
                Cotisation.date_paiement >= today.replace(day=1),
                Cotisation.statut == 'Payé'
            ).first()
            
            if not cotisation_mois and membre.email:
                # Envoyer rappel
                if send_cotisation_reminder(membre, echeance, 50.00):  # Montant standard
                    rappel_envoye += 1
        
        print(f"✅ {rappel_envoye} rappels de cotisation envoyés")
        return rappel_envoye