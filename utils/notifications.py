# utils/notifications.py
from flask_mail import Message
from flask import render_template, current_app, url_for
import logging

logger = logging.getLogger(__name__)

def send_email(subject, recipients, text_body, html_body=None):
    """
    Envoie un email à un ou plusieurs destinataires
    """
    try:
        # ← IMPORT LAZY : Importer mail ici, pas en haut du fichier
        from app import mail
        
        msg = Message(
            subject=subject,
            recipients=recipients,
            body=text_body,
            html=html_body,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        mail.send(msg)
        logger.info(f"✅ Email envoyé à {recipients}: {subject}")
        return True
    except Exception as e:
        logger.error(f"❌ Erreur envoi email: {e}")
        return False

def send_welcome_email(membre, mot_de_passe_temporaire):
    """
    Email de bienvenue pour un nouveau membre, avec son mot de passe temporaire.

    Paramètres :
        membre : instance Membre (déjà créée en base, avec nom/prenom/email)
        mot_de_passe_temporaire : str — le mot de passe en clair généré pour
            ce membre. Il n'existe qu'à cet instant précis (ailleurs, seul le
            hash est stocké) : c'est pour ça qu'il faut le passer explicitement
            ici, juste après la création du compte.
    """
    subject = "🎉 Bienvenue à la Mutuelle Solidaire !"
    recipients = [membre.email]

    # url_for(..., _external=True) construit une URL absolue (avec http://...)
    # plutôt qu'un chemin relatif — indispensable dans un email, qui n'a pas
    # de contexte de page courante comme un navigateur.
    url_login = url_for('login', _external=True)

    text_body = f"""
Bonjour {membre.prenom} {membre.nom},

Bienvenue à la Mutuelle Solidaire !

Votre compte a été créé avec succès. Voici vos identifiants de connexion :
- Email : {membre.email}
- Mot de passe temporaire : {mot_de_passe_temporaire}
- URL : {url_login}

⚠️ Pour des raisons de sécurité, vous devrez changer ce mot de passe dès
votre première connexion.

Cordialement,
La Mutuelle Solidaire
    """

    try:
        html_body = render_template(
            'emails/welcome.html',
            membre=membre,
            mot_de_passe_temporaire=mot_de_passe_temporaire,
            url_login=url_login,
        )
    except Exception as e:
        logger.error(f"⚠️ Template welcome.html introuvable ou en erreur : {e}")
        html_body = None

    return send_email(subject, recipients, text_body, html_body)

def send_cotisation_confirmation(membre, cotisation):
    """Confirmation de paiement de cotisation"""
    subject = "✅ Cotisation Enregistrée - Mutuelle Solidaire"
    recipients = [membre.email]

    # cotisation.date_paiement est un datetime (voir le modèle Cotisation) ;
    # on protège le formatage au cas où elle serait absente (None).
    date_fmt = cotisation.date_paiement.strftime('%d/%m/%Y') if cotisation.date_paiement else 'Non spécifiée'

    text_body = f"""
Bonjour {membre.prenom} {membre.nom},

Nous confirmons la bonne réception de votre cotisation.

Détails de la cotisation :
- Type        : {cotisation.type_cotisation or 'Non spécifié'}
- Montant      : {cotisation.montant} FCFA
- Date de paiement : {date_fmt}
- Mode de paiement  : {cotisation.mode_paiement or 'Non spécifié'}
- Référence    : {cotisation.reference_transaction or 'N/A'}

Merci pour votre confiance et votre engagement envers la mutuelle.

Cordialement,
La Mutuelle Solidaire
    """

    try:
        html_body = render_template(
            'emails/cotisation_confirmation.html',
            membre=membre,
            cotisation=cotisation,
            date_fmt=date_fmt,
        )
    except Exception as e:
        logger.error(f"⚠️ Template cotisation_confirmation.html introuvable ou en erreur : {e}")
        html_body = None

    return send_email(subject, recipients, text_body, html_body)
