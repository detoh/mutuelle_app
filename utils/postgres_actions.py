# utils/postgres_actions.py
from app import db
from sqlalchemy import text

def ajouter_membre(nom, prenom, email, password_hash, **kwargs):
    result = db.session.execute(text("""
        SELECT ajouter_membre_securise(
            :nom, :prenom, :email, :telephone, :fonction, :service, :emploi, :date_adhesion, :password_hash
        )
    """), {
        'nom': nom, 'prenom': prenom, 'email': email, 'password_hash': password_hash,
        'telephone': kwargs.get('telephone'),
        'fonction': kwargs.get('fonction'),
        'service': kwargs.get('service'),
        'emploi': kwargs.get('emploi'),
        'date_adhesion': kwargs.get('date_adhesion')
    })
    db.session.commit()
    return result.scalar()

def valider_cotisations_mois(periode):
    result = db.session.execute(text("SELECT valider_cotisations_par_periode(:p)"), {'p': periode})
    db.session.commit()
    return result.scalar()

def attribuer_aide(membre_id, type_aide, montant, description):
    result = db.session.execute(text("""
        SELECT attribuer_aide_intelligente(:membre_id, :type_aide, :montant, :description)
    """), {
        'membre_id': membre_id, 'type_aide': type_aide, 
        'montant': montant, 'description': description
    })
    db.session.commit()
    return result.scalar()

def generer_rapport(annee, mois):
    result = db.session.execute(text("SELECT * FROM generer_rapport_mensuel(:annee, :mois)"), 
                                {'annee': annee, 'mois': mois})
    return result.mappings().first()

def maintenance_db():
    result = db.session.execute(text("SELECT * FROM maintenance_nettoyage()"))
    db.session.commit()
    return result.fetchall()