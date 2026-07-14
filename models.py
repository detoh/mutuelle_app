# models.py — PostgreSQL + Procédures & Fonctions Financières
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text, bindparam, Integer

db = SQLAlchemy()

# ─────────────────────────────────────────────────────────────
# MODÈLES ORM
# ─────────────────────────────────────────────────────────────

class Membre(UserMixin, db.Model):
    __tablename__ = 'membres'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    telephone = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True, nullable=False)
    ville = db.Column(db.String(200))
    password_hash = db.Column(db.String(200))
    date_adhesion = db.Column(db.Date, nullable=True)
    statut = db.Column(db.String(20), default='Actif')
    is_admin = db.Column(db.Boolean, default=False)
    is_comptable = db.Column(db.Boolean, default=False)
    fonction = db.Column(db.String(100))
    photo = db.Column(db.String(200))
    service = db.Column(db.String(100))
    emploi = db.Column(db.String(100))
    doit_changer_mot_de_passe = db.Column(db.Boolean, default=True, nullable=False) #vient d'etre ajouter
    cotisations = db.relationship('Cotisation', backref='membre', lazy=True)
    aides_recues = db.relationship('Aide', foreign_keys='Aide.membre_id', backref='beneficiaire', lazy=True)

    def set_password(self, p):
        self.password_hash = generate_password_hash(p)

    def check_password(self, p):
        return check_password_hash(self.password_hash, p)

    @staticmethod
    def creer(nom, prenom, email, telephone, fonction, service,
              emploi, date_adhesion, password_hash, is_admin=False):
        db.session.execute(text("""
            CALL sp_creer_membre(:nom,:prenom,:email,:telephone,:fonction,
                                 :service,:emploi,:date_adhesion,:password_hash,:is_admin)
        """), dict(nom=nom, prenom=prenom, email=email, telephone=telephone,
                  fonction=fonction, service=service, emploi=emploi,
                  date_adhesion=date_adhesion, password_hash=password_hash,
                  is_admin=is_admin))
        db.session.commit()
        return Membre.query.filter_by(email=email).first()

    def modifier(self, nom, prenom, telephone, ville, fonction, service, emploi, statut):
        db.session.execute(text("""
            CALL sp_modifier_membre(:id,:nom,:prenom,:telephone,:ville,
                                    :fonction,:service,:emploi,:statut)
        """), dict(id=self.id, nom=nom, prenom=prenom, telephone=telephone,
                  ville=ville, fonction=fonction, service=service,
                  emploi=emploi, statut=statut))
        db.session.commit()
        db.session.refresh(self)

    def supprimer(self):
        db.session.execute(text("CALL sp_supprimer_membre(:id)"), {'id': self.id})
        db.session.commit()

    def changer_password(self, nouveau):
        h = generate_password_hash(nouveau)
        db.session.execute(text("CALL sp_changer_password(:id,:hash)"),
                           {'id': self.id, 'hash': h})
        db.session.commit()
        self.password_hash = h

    def toggle_comptable(self):
        db.session.execute(text("CALL sp_toggle_comptable(:id)"), {'id': self.id})
        db.session.commit()
        db.session.refresh(self)

    def maj_photo(self, photo_path):
        db.session.execute(text("CALL sp_maj_photo_membre(:id,:photo)"),
                           {'id': self.id, 'photo': photo_path})
        db.session.commit()
        self.photo = photo_path

    def tableau_de_bord(self):
        """Retourne les stats financières du membre via fn_tableau_bord_membre."""
        stmt = text("SELECT * FROM fn_tableau_bord_membre(:id)").bindparams(
            bindparam("id", type_=Integer)
        )
        result = db.session.execute(stmt, {"id": self.id})
        row = result.fetchone()

        if row and row._mapping:
            m = row._mapping
            return {
                'total_cotise': float(m.get('total_cotise') or 0),
                'nb_cotisations': m.get('nb_cotisations') or 0,
                'derniere_cotisation': m.get('derniere_cotisation'),
                'total_aides_recues': float(m.get('total_aides_recues') or 0),
                'nb_aides': m.get('nb_aides') or 0,
                'solde_membre': float(m.get('solde_membre') or 0),
                'statut_cotisation': m.get('statut_cotisation', 'Inconnu'),
            }
        return {}


class Cotisation(db.Model):
    __tablename__ = 'cotisations'  
    
    id = db.Column(db.Integer, primary_key=True)
    membre_id = db.Column(db.Integer, db.ForeignKey('membres.id'), nullable=False)
    type_cotisation = db.Column(db.String(50))
    montant = db.Column(db.Numeric(10, 2), nullable=False)
    date_paiement = db.Column(db.DateTime, default=datetime.utcnow)
    statut = db.Column(db.String(20), default='en_attente')
    date_echeance = db.Column(db.Date, nullable=True)
    mode_paiement = db.Column(db.String(50), nullable=True)
    type_paiement = db.Column(db.String(50), nullable=True)
    telephone = db.Column(db.String(20), nullable=True)
    reference_transaction = db.Column(db.String(100), nullable=True)

    @staticmethod
    def enregistrer(membre_id, type_cotisation, montant, date_paiement):
        db.session.execute(text("""
            CALL sp_enregistrer_cotisation(:membre_id,:type_cotisation,:montant,:date_paiement)
        """), dict(membre_id=membre_id, type_cotisation=type_cotisation,
                   montant=montant, date_paiement=date_paiement))
        db.session.commit()

    def to_dict(self):
        # 1. Gestion ultra-sécurisée de la date
        date_fmt = ''
        if self.date_paiement:
            try:
                # Maintenant que 'date' est importé en haut, ceci fonctionnera
                if isinstance(self.date_paiement, (date, datetime)):
                    date_fmt = self.date_paiement.strftime('%d/%m/%Y')
                else:
                    date_fmt = str(self.date_paiement)
            except Exception:
                # Fallback ultime si le format est vraiment étrange
                date_fmt = str(self.date_paiement)

        return {
            'id': self.id,
            'membre_id': self.membre_id,
            'montant': float(self.montant) if self.montant is not None else 0.0,
            'date_paiement': date_fmt,
            'type_paiement': self.type_paiement or 'Non spécifié',
            'mode_paiement': self.mode_paiement or 'Manuel',
            'telephone': self.telephone or '',
            'statut': self.statut or 'en_attente',
            'reference': self.reference_transaction or ''
        }

    def supprimer(self):
        db.session.execute(text("CALL sp_supprimer_cotisation(:id)"), {'id': self.id})
        db.session.commit()

    @property
    def nom_complet(self):
        """Retourne le nom et prénom combinés, gère les espaces et les None."""
        parts = [self.nom, self.prenom]
        # Garde uniquement les parties qui ne sont pas None ou vides
        return " ".join(part.strip() for part in parts if part).strip()
        

        
class Aide(db.Model):
    __tablename__ = 'aides'
    id = db.Column(db.Integer, primary_key=True)
    membre_id = db.Column(db.Integer, db.ForeignKey('membres.id'), nullable=False)
    type_aide = db.Column(db.String(50))
    montant = db.Column(db.Numeric(10, 2), nullable=False)
    date_attribution = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text)
    valide_par_admin = db.Column(db.Boolean, default=True)
    valide_par_comptable = db.Column(db.Boolean, default=False)
    valideur_id = db.Column(db.Integer, db.ForeignKey('membres.id'), nullable=True)

    valideur = db.relationship('Membre', foreign_keys=[valideur_id])

    @staticmethod
    def attribuer(membre_id, type_aide, montant, description, date_attribution=None,
                  valideur_id=None, valide_par_admin=True, valide_par_comptable=False):
        date_final = date_attribution or datetime.utcnow()

        db.session.execute(text("""
            CALL sp_attribuer_aide(:membre_id, :type_aide, :montant, :description,
                                   :date_attribution, :valideur_id, :valide_par_admin,
                                   :valide_par_comptable)
        """), dict(
            membre_id=membre_id,
            type_aide=type_aide,
            montant=montant,
            description=description,
            date_attribution=date_final,
            valideur_id=valideur_id,
            valide_par_admin=valide_par_admin,
            valide_par_comptable=valide_par_comptable
        ))
        db.session.commit()

    def supprimer(self):
        db.session.execute(text("CALL sp_supprimer_aide(:id)"), {'id': self.id})
        db.session.commit()

class Evenement(db.Model):
    __tablename__ = 'evenements'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100))
    budget_prevu = db.Column(db.Float)
    depenses_reelles = db.Column(db.Float, default=0.0)
    date = db.Column(db.DateTime)
    description = db.Column(db.Text)
    statut = db.Column(db.Boolean, default=True, nullable=False)

    @staticmethod
    def creer(nom, budget_prevu, depenses_reelles, date, description, statut=True):
        db.session.execute(text("""
            CALL sp_creer_evenement(:nom, :budget_prevu, :depenses_reelles, :date, :description, :statut)
        """), dict(
            nom=nom, 
            budget_prevu=budget_prevu,
            depenses_reelles=depenses_reelles, 
            date=date,
            description=description,
            statut=statut  # ➕ Paramètre ajouté
        ))
        db.session.commit()

    def modifier(self, nom, budget_prevu, depenses_reelles, date, description, statut=True):
        db.session.execute(text("""
            CALL sp_modifier_evenement(:id, :nom, :budget_prevu, :depenses_reelles, :date, :description, :statut)
        """), dict(
            id=self.id, 
            nom=nom, 
            budget_prevu=budget_prevu,
            depenses_reelles=depenses_reelles, 
            date=date,
            description=description,
            statut=statut  # ➕ Paramètre ajouté
        ))
        db.session.commit()
        db.session.refresh(self)

    def supprimer(self):
        db.session.execute(text("CALL sp_supprimer_evenement(:id)"), {'id': self.id})
        db.session.commit()




class Don(db.Model):
    __tablename__ = 'dons'
    id = db.Column(db.Integer, primary_key=True)
    donateur_nom = db.Column(db.String(100))
    montant = db.Column(db.Numeric(10, 2), nullable=False)      
    date = db.Column(db.DateTime, default=datetime.utcnow)
    statut = db.Column(db.Boolean, default=False, nullable=False) # Votre nouvelle colonne

    @staticmethod
    def enregistrer(donateur_nom, montant, statut=False):
        # On ajoute le paramètre :statut à l'appel de la procédure stockée
        db.session.execute(
            text("CALL sp_enregistrer_don(:donateur_nom, :montant, :statut)"),
            {
                'donateur_nom': donateur_nom, 
                'montant': montant,
                'statut': statut # On passe le booléen Python
            }
        )
        db.session.commit()

    def supprimer(self):
        db.session.execute(text("CALL sp_supprimer_don(:id)"), {'id': self.id})
        db.session.commit()


class AssistanceEvenement(db.Model):
    """Demandes d'assistance pour événements familiaux (Décès, Naissance, Mariage,Maladie,Accident,Retraite,Mutation,Autre)."""
    __tablename__ = 'assistance_evenements'
    
    # Constantes utilisées dans app.py
    TYPE_DECES = 'Deces'
    TYPE_NAISSANCE = 'Naissance'
    TYPE_MARIAGE = 'Mariage'
    TYPE_MAlALADIE = 'Maladie'
    TYPE_ACCIDENT = 'Accident'
    TYPE_RETRAITE = 'Retraite'
    TYPE_MUTATION = 'Mutation'
    TYPE_AUTRE = 'Autres'
    
    id = db.Column(db.Integer, primary_key=True)
    membre_id = db.Column(db.Integer, db.ForeignKey('membres.id'), nullable=False)
    famille_id = db.Column(db.Integer, db.ForeignKey('famille_membres.id'), nullable=True)
    type_evenement = db.Column(db.String(20), nullable=False, default=TYPE_DECES)
    date_evenement = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(100), nullable=False)
    montant_prevu = db.Column(db.Numeric(10, 2), nullable=False)
    montant_versee = db.Column(db.Numeric(10, 2), nullable=True)
    statut = db.Column(db.String(20), default='En attente')
    signature_unique = db.Column(db.String(100), unique=True, nullable=False)
    piece_jointe_path = db.Column(db.String(200), nullable=True)
    demande_le = db.Column(db.DateTime, default=datetime.utcnow)
    valide_par = db.Column(db.Integer, db.ForeignKey('membres.id'), nullable=True)
    date_validation = db.Column(db.DateTime, nullable=True)
    date_paiement = db.Column(db.DateTime, nullable=True)
    motif_refus = db.Column(db.String(200), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    # Relations
    membre = db.relationship('Membre', foreign_keys=[membre_id],
                             backref='assistances_demandees', lazy=True)
    valideur = db.relationship('Membre', foreign_keys=[valide_par],
                               backref='assistances_validees', lazy=True)
    famille = db.relationship('FamilleMembre', backref='assistances_associees', lazy=True)

    STATUTS_VALIDES = ['En attente', 'Validée', 'Refusée', 'Versée']

    @staticmethod
    def creer_demande(membre_id, type_evenement, date_evenement, description=None,
                      montant_prevu=0, famille_id=None, lien_parente=None,
                      piece_path=None, notes=None):
        """Crée une demande d'assistance et retourne (objet, is_new)."""
        db.session.execute(text("""
            CALL sp_creer_assistance_evenement(
                :membre_id, :famille_id, :type_evenement, :date_evenement,
                :description, :montant_prevu, :piece_jointe_path, :notes
            )
        """), dict(
            membre_id=membre_id,
            famille_id=famille_id,
            type_evenement=type_evenement,
            date_evenement=date_evenement,
            description=description or '',
            montant_prevu=montant_prevu,
            piece_jointe_path=piece_path,
            notes=notes
        ))
        db.session.commit()
        # Récupère l'objet fraîchement créé
        new_assistance = AssistanceEvenement.query.filter_by(
            membre_id=membre_id, type_evenement=type_evenement, 
            date_evenement=date_evenement
        ).order_by(AssistanceEvenement.id.desc()).first()
        return new_assistance, True

    def valider(self, valideur_id, montant_versee=None, notes=None):
        db.session.execute(text("""
            CALL sp_valider_assistance_evenement(
                CAST(:id AS INTEGER),
                CAST(:valideur_id AS INTEGER),
                CAST(:montant_versee AS NUMERIC),
                CAST(:notes AS TEXT)
            )
        """), dict(
            id=int(self.id),
            valideur_id=int(valideur_id),
            montant_versee=float(montant_versee or self.montant_prevu or 0),
            notes=str(notes) if notes else None
        ))
        db.session.commit()
        db.session.refresh(self)

    def refuser(self, valideur_id, motif_refus):
        db.session.execute(text("""
            CALL sp_refuser_assistance_evenement(
                CAST(:id AS INTEGER),
                CAST(:valideur_id AS INTEGER),
                CAST(:motif_refus AS TEXT)
            )
        """), dict(
            id=int(self.id),
            valideur_id=int(valideur_id),
            motif_refus=str(motif_refus)
        ))
        db.session.commit()
        db.session.refresh(self)

    def marquer_versee(self, date_paiement=None):
        db.session.execute(text("""
            CALL sp_verser_assistance_evenement(
                CAST(:id AS INTEGER),
                CAST(:date_paiement AS TIMESTAMP)
            )
        """), dict(
            id=int(self.id),
            date_paiement=date_paiement or datetime.utcnow()
        ))
        db.session.commit()
        db.session.refresh(self)

    def supprimer(self):
        db.session.execute(text("CALL sp_supprimer_assistance_evenement(:id)"), {'id': self.id})
        db.session.commit()

    @property
    def montant_final(self):
        return self.montant_versee if self.montant_versee is not None else self.montant_prevu

    @property
    def est_en_attente(self): return self.statut == 'En attente'
    @property
    def est_validee(self): return self.statut == 'Validée'
    @property
    def est_versee(self): return self.statut == 'Versée'

    @property
    def badge_couleur(self):
        return {
            'En attente': 'warning', 'Validée': 'info',
            'Versée': 'success', 'Refusée': 'danger',
        }.get(self.statut, 'secondary')

    def __repr__(self):
        return f'<AssistanceEvenement {self.type_evenement} membre={self.membre_id} statut={self.statut}>'


class Projet(db.Model):
    __tablename__ = 'projets'
    idprojet = db.Column(db.Integer, primary_key=True)
    titreprojet = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    datedebut = db.Column(db.DateTime)
    datefiprojet = db.Column(db.DateTime)
    coutexecution = db.Column(db.Float, default=0.0)
    nomdonateur = db.Column(db.String(200))
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    statut = db.Column(db.String(20), default='En cours')

    @staticmethod
    def creer(titreprojet, description, datedebut, datefiprojet,
              coutexecution, nomdonateur, statut):
        db.session.execute(text("""
            CALL sp_creer_projet(:titreprojet,:description,:datedebut,:datefiprojet,
                                 :coutexecution,:nomdonateur,:statut)
        """), dict(titreprojet=titreprojet, description=description,
                   datedebut=datedebut, datefiprojet=datefiprojet,
                   coutexecution=coutexecution, nomdonateur=nomdonateur, statut=statut))
        db.session.commit()

    def modifier(self, titreprojet, description, datedebut, datefiprojet,
                 coutexecution, nomdonateur, statut):
        db.session.execute(text("""
            CALL sp_modifier_projet(:id,:titreprojet,:description,:datedebut,
                                    :datefiprojet,:coutexecution,:nomdonateur,:statut)
        """), dict(id=self.idprojet, titreprojet=titreprojet,
                   description=description, datedebut=datedebut,
                   datefiprojet=datefiprojet, coutexecution=coutexecution,
                   nomdonateur=nomdonateur, statut=statut))
        db.session.commit()
        db.session.refresh(self)

    def supprimer(self):
        db.session.execute(text("CALL sp_supprimer_projet(:id)"), {'id': self.idprojet})
        db.session.commit()


class BilanAnnuel(db.Model):
    __tablename__ = 'bilan_annuel'
    id = db.Column(db.Integer, primary_key=True)
    annee = db.Column(db.Integer, unique=True, nullable=False)
    total_cotisations = db.Column(db.Numeric(12, 2), default=0)
    total_dons = db.Column(db.Numeric(12, 2), default=0)
    total_aides = db.Column(db.Numeric(12, 2), default=0)
    total_evenements = db.Column(db.Numeric(12, 2), default=0)
    total_projets = db.Column(db.Numeric(12, 2), default=0)
    total_entrees = db.Column(db.Numeric(12, 2), default=0)
    total_sorties = db.Column(db.Numeric(12, 2), default=0)
    solde_net = db.Column(db.Numeric(12, 2), default=0)
    nb_membres_actifs = db.Column(db.Integer, default=0)
    date_cloture = db.Column(db.DateTime, default=datetime.utcnow)
    clos_par = db.Column(db.Text)


class FamilleMembre(db.Model):
    """Modèle représentant un membre de la famille dans la mutuelle"""
    __tablename__ = 'famille_membres'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    membre_id = db.Column(db.Integer, db.ForeignKey('membres.id', ondelete='CASCADE'), nullable=False, index=True)
    nom = db.Column(db.String(50), nullable=False)
    prenom = db.Column(db.String(50), nullable=False)
    lien_parente = db.Column(db.String(30), nullable=False)
    date_naissance = db.Column(db.Date)
    date_deces = db.Column(db.Date)
    date_ajout = db.Column(db.DateTime, default=db.func.now())
    telephone = db.Column(db.String(20))
    adresse = db.Column(db.Text)
    est_a_charge = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    parent1_membre_id = db.Column(db.Integer, db.ForeignKey('famille_membres.id', ondelete='SET NULL'), nullable=True)
    parent2_membre_id = db.Column(db.Integer, db.ForeignKey('famille_membres.id', ondelete='SET NULL'), nullable=True)

    membre_principal = db.relationship('Membre', backref=db.backref('membres_famille', lazy='dynamic', cascade='all, delete-orphan'), foreign_keys=[membre_id])
    parent1 = db.relationship('FamilleMembre', remote_side=[id], foreign_keys=[parent1_membre_id], backref='enfants_parent1')
    parent2 = db.relationship('FamilleMembre', remote_side=[id], foreign_keys=[parent2_membre_id], backref='enfants_parent2')

    @property
    def age(self):
        if not self.date_naissance: return None
        from datetime import date
        today = date.today()
        age = today.year - self.date_naissance.year
        if (today.month, today.day) < (self.date_naissance.month, self.date_naissance.day):
            age -= 1
        return age

    @property  
    def age(self):
        """Calcule l'âge du membre si date_naissance est renseignée"""
        if not self.date_naissance:
            return None
        from datetime import date
        today = date.today()
        age_calc = today.year - self.date_naissance.year
        if (today.month, today.day) < (self.date_naissance.month, self.date_naissance.day):
            age_calc -= 1
        return age_calc
    @property
    def est_majeur(self):
        return self.age is not None and self.age >= 18
    @property
    def est_majeur(self): return self.age is not None and self.age >= 18
    @property
    def est_vivant(self): return self.date_deces is None
    
    # Propriété attendue par app.py
    @property
    def est_enfant_membres(self):
        return self.lien_parente == 'Enfant' and self.parent1_membre_id and self.parent2_membre_id

    def __repr__(self):
        statut = "†" if self.date_deces else ""
        return f"<FamilleMembre {self.prenom} {self.nom} ({self.lien_parente}) {statut}>"

class ParametresMutuelle(db.Model):
    __tablename__ = 'parametres_mutuelle'

    NB_ECHEANCES_PAR_FREQUENCE = {
        'mensuelle': 12,
        'trimestrielle': 4,
        'semestrielle': 2,
    }

    id = db.Column(db.Integer, primary_key=True)
    frequence_cotisation = db.Column(db.String(20), nullable=False, default='mensuelle')
    montant_cotisation_annuel = db.Column(db.Numeric(10, 2), nullable=False, default=0)

    @staticmethod
    def get():
        """Récupère la ligne unique de paramètres (id=1). La crée si absente."""
        params = ParametresMutuelle.query.get(1)
        if params is None:
            params = ParametresMutuelle(id=1, frequence_cotisation='mensuelle', montant_cotisation_annuel=0)
            db.session.add(params)
            db.session.commit()
        return params

    @property
    def nb_echeances_par_an(self):
        return self.NB_ECHEANCES_PAR_FREQUENCE.get(self.frequence_cotisation, 12)

    @property
    def montant_par_echeance(self):
        """Montant attendu à chaque échéance, arrondi à 2 décimales."""
        nb = self.nb_echeances_par_an
        if nb == 0 or self.montant_cotisation_annuel is None:
            return 0
        return round(float(self.montant_cotisation_annuel) / nb, 2)

    def modifier(self, frequence_cotisation, montant_cotisation_annuel):
        if frequence_cotisation not in self.NB_ECHEANCES_PAR_FREQUENCE:
            raise ValueError(f"Fréquence invalide : {frequence_cotisation}")
        self.frequence_cotisation = frequence_cotisation
        self.montant_cotisation_annuel = montant_cotisation_annuel
        db.session.commit()

# ─────────────────────────────────────────────────────────────
# FONCTIONS UTILITAIRES
# ─────────────────────────────────────────────────────────────
def calculer_solde_caisse(annee=None):
    try:
        # ➕ AJOUT DU CAST(:annee AS INTEGER) pour éviter l'erreur AmbiguousFunction avec NULL
        row = db.session.execute(
            text("SELECT * FROM fn_solde_caisse(CAST(:annee AS INTEGER))"), 
            {'annee': annee}
        ).fetchone()
        
        if row and row._mapping:
            m = row._mapping
            return float(m['total_entrees'] or 0), float(m['total_sorties'] or 0), float(m['solde'] or 0)
        return 0.0, 0.0, 0.0
    except Exception as e:
        print(f"❌ ERREUR SQL SOLDE: {e}") # Affichage dans la console pour debug
        return 0.0, 0.0, 0.0

def get_bilan_annuel(annee):
    try:
        row = db.session.execute(text("SELECT * FROM fn_bilan_annuel(:annee)"), {'annee': annee}).fetchone()
    except Exception as e:
        print(f"❌ ERREUR SQL BILAN: {e}") # Affichage dans la console pour debug
        return {}

    if row and row._mapping:
        m = row._mapping
        return {
            'annee': m.get('annee'), 'total_cotisations': float(m.get('total_cotisations') or 0),
            'total_dons': float(m.get('total_dons') or 0), 'total_entrees': float(m.get('total_entrees') or 0),
            'total_aides': float(m.get('total_aides') or 0), 'total_evenements': float(m.get('total_evenements') or 0),
            'total_projets': float(m.get('total_projets') or 0), 'total_sorties': float(m.get('total_sorties') or 0),
            'solde_net': float(m.get('solde_net') or 0), 'nb_cotisations': m.get('nb_cotisations', 0),
            'nb_membres_actifs': m.get('nb_membres_actifs', 0), 'nb_aides': m.get('nb_aides', 0),
            'nb_dons': m.get('nb_dons', 0),
        }
    return {}

def get_recent_transactions(limit=10):
    from datetime import date as _date
    icon_map  = {'cotisation': 'fa-coins', 'aide': 'fa-hand-holding-heart',
                 'don': 'fa-gift', 'assistance': 'fa-calendar-alt', 'evenement': 'fa-calendar-check'}
    color_map = {'cotisation': 'success', 'aide': 'danger',
                 'don': 'info', 'assistance': 'warning', 'evenement': 'secondary'}

    # ── 1. Cotisations / Aides / Dons via fonction PostgreSQL ──
    rows = db.session.execute(
        text("SELECT * FROM fn_transactions_recentes(:limit)"),
        {'limit': limit}
    ).fetchall()

    transactions = [{
        'id':      r._mapping.get('id'),
        'type_op': r._mapping.get('type_op', ''),
        'subtype': r._mapping.get('subtype', ''),
        'membre':  r._mapping.get('membre', ''),
        'montant': float(r._mapping.get('montant') or 0),
        'signe':   r._mapping.get('signe', '+'),
        'date_op': r._mapping.get('date_op'),
        'statut':  r._mapping.get('statut', ''),
        'periode': r._mapping.get('periode', ''),
        'icon':    icon_map.get(r._mapping.get('type_op', ''), 'fa-circle'),
        'color':   color_map.get(r._mapping.get('type_op', ''), 'secondary'),
    } for r in rows]

    # ── 2. Assistances événements (Décès, Naissance, Mariage) ──
    from sqlalchemy.orm import joinedload
    assistances = (AssistanceEvenement.query
                   .options(joinedload(AssistanceEvenement.membre))
                   .order_by(AssistanceEvenement.demande_le.desc())
                   .limit(limit).all())

    for a in assistances:
        nom_membre = (f"{a.membre.nom} {a.membre.prenom}".strip()
                      if a.membre else '—')
        montant = float(a.montant_versee or a.montant_prevu or 0)
        transactions.append({
            'id':      a.id,
            'type_op': 'assistance',
            'subtype': a.type_evenement,
            'membre':  nom_membre,
            'montant': montant,
            'signe':   '-',
            'date_op': a.date_evenement,
            'statut':  a.statut,
            'periode': '',
            'icon':    icon_map['assistance'],
            'color':   color_map['assistance'],
        })

    # ── 3. Événements (dépenses réelles) ──
    evenements = (Evenement.query
                  .order_by(Evenement.date.desc())
                  .limit(limit).all())

    for e in evenements:
        depenses = float(e.depenses_reelles or 0)
        if depenses > 0:
            transactions.append({
                'id':      e.id,
                'type_op': 'evenement',
                'subtype': e.nom,
                'membre':  '—',
                'montant': depenses,
                'signe':   '-',
                'date_op': e.date,
                'statut':  'Validée' if e.statut else 'En attente',
                'periode': '',
                'icon':    icon_map['evenement'],
                'color':   color_map['evenement'],
            })

    # ── 4. Tri global : normalise date/datetime → datetime pour éviter TypeError ──
    def _to_dt(d):
        if d is None:
            return datetime.min
        # date seule (ex: AssistanceEvenement.date_evenement) → datetime
        if type(d) is _date:
            return datetime(d.year, d.month, d.day)
        return d  # déjà un datetime

    transactions.sort(key=lambda t: _to_dt(t['date_op']), reverse=True)
    return transactions[:limit]

def get_monthly_flow_data(months=12):
    rows = db.session.execute(text("SELECT * FROM fn_flux_mensuels(:mois)"), {'mois': months}).fetchall()
    return [{
        'label_fr': r._mapping.get('mois_label', ''), 'label': r._mapping.get('annee_mois') or r._mapping.get('mois') or r._mapping.get('periode', ''),
        'entrees': float(r._mapping.get('entrees') or 0), 'sorties': float(r._mapping.get('sorties') or 0), 'solde': float(r._mapping.get('solde') or 0),
        'cotisations': float(r._mapping.get('cotisations') or 0), 'dons': float(r._mapping.get('dons') or 0),
        'aides': float(r._mapping.get('aides') or 0), 'evenements': float(r._mapping.get('evenements') or 0),
    } for r in rows]

def get_comparaison_annuelle(annee):
    rows = db.session.execute(text("SELECT * FROM fn_comparaison_annuelle(:annee)"), {'annee': annee}).fetchall()
    return [{
        'categorie': r._mapping.get('categorie', ''), 'montant_annee': float(r._mapping.get('montant_annee') or 0),
        'montant_annee_prec': float(r._mapping.get('montant_annee_prec') or 0), 'variation': float(r._mapping.get('variation') or 0),
        'variation_pct': float(r._mapping.get('variation_pct') or 0),
    } for r in rows]

def get_top_cotisants(annee=None, limit=10):
    rows = db.session.execute(text("SELECT * FROM fn_top_cotisants(:annee, :limit)"), {'annee': annee, 'limit': limit}).fetchall()
    return [{
        'rang': r._mapping.get('rang', 0), 'membre_id': r._mapping.get('membre_id'), 'nom_complet': r._mapping.get('nom_complet', ''),
        'email': r._mapping.get('email', ''), 'total_cotise': float(r._mapping.get('total_cotise') or 0),
        'nb_paiements': r._mapping.get('nb_paiements', 0), 'derniere_cotisation': r._mapping.get('derniere_cotisation'),
    } for r in rows]

def get_cotisations_par_membre(annee):
    """Retourne TOUS les membres actifs avec leur total de cotisations payées
    pour l'année donnée (0 si aucune cotisation), via fn_cotisations_par_membre_annee."""
    rows = db.session.execute(
        text("SELECT * FROM fn_cotisations_par_membre_annee(:annee)"), {'annee': annee}
    ).fetchall()
    return [{
        'membre_id': r._mapping.get('membre_id'),
        'nom_complet': r._mapping.get('nom_complet', ''),
        'email': r._mapping.get('email', ''),
        'total_cotise': float(r._mapping.get('total_cotise') or 0),
        'nb_paiements': r._mapping.get('nb_paiements', 0),
        'derniere_cotisation': r._mapping.get('derniere_cotisation'),
    } for r in rows]

def get_aides_assistances_par_membre(annee):
    """Retourne les membres ayant reçu au moins une aide validée ou une assistance
    versée pour l'année donnée, avec le détail des deux sources et le total combiné,
    via fn_aides_assistances_par_membre_annee."""
    rows = db.session.execute(
        text("SELECT * FROM fn_aides_assistances_par_membre_annee(:annee)"), {'annee': annee}
    ).fetchall()
    return [{
        'membre_id': r._mapping.get('membre_id'),
        'nom_complet': r._mapping.get('nom_complet', ''),
        'email': r._mapping.get('email', ''),
        'total_aides': float(r._mapping.get('total_aides') or 0),
        'nb_aides': r._mapping.get('nb_aides', 0),
        'total_assistances': float(r._mapping.get('total_assistances') or 0),
        'nb_assistances': r._mapping.get('nb_assistances', 0),
        'total_combine': float(r._mapping.get('total_combine') or 0),
        'derniere_date': r._mapping.get('derniere_date'),
    } for r in rows]

def get_membres_en_retard(mois_retard=None):
    """
    Retourne les membres actifs n'ayant pas cotisé depuis au moins
    `mois_retard` mois. Si `mois_retard` n'est pas précisé, utilise le
    nombre de mois correspondant à une échéance selon la fréquence de
    cotisation configurée (1 mois si mensuelle, 3 si trimestrielle,
    6 si semestrielle).
    """
    if mois_retard is None:
        parametres = ParametresMutuelle.get()
        mois_retard = 12 // parametres.nb_echeances_par_an

    rows = db.session.execute(text("SELECT * FROM fn_membres_en_retard(:mois)"), {'mois': mois_retard}).fetchall()
    return [{
        'membre_id': r._mapping.get('membre_id'), 'nom_complet': r._mapping.get('nom_complet', ''),
        'email': r._mapping.get('email', ''), 'telephone': r._mapping.get('telephone', ''),
        'derniere_cotisation': r._mapping.get('derniere_cotisation'), 'mois_sans_cotisation': r._mapping.get('mois_sans_cotisation', 0),
    } for r in rows]

def cloturer_exercice(annee, clos_par='système'):
    db.session.execute(text("CALL sp_cloturer_exercice(:annee, :clos_par)"), {'annee': annee, 'clos_par': clos_par})
    db.session.commit()

def rafraichir_dashboard():
    db.session.execute(text("CALL sp_rafraichir_dashboard()"))
    db.session.commit()

import calendar
from sqlalchemy import func

def get_etat_cotisations_membres(annee=None):
    """
    Retourne, pour chaque membre actif, l'état de ses cotisations sur
    l'année : une ligne par échéance (selon la fréquence configurée),
    le total payé, le total attendu, le solde et un statut à jour/pas à jour.
    """
    if annee is None:
        annee = datetime.now().year

    parametres = ParametresMutuelle.get()
    nb_echeances = parametres.nb_echeances_par_an
    montant_echeance = float(parametres.montant_par_echeance)
    mois_par_periode = 12 // nb_echeances

    # Membres en retard (même logique que la page "membres en retard")
    ids_en_retard = {r['membre_id'] for r in get_membres_en_retard()}

    membres = Membre.query.filter_by(statut='Actif').order_by(Membre.nom, Membre.prenom).all()
    etat = []

    for m in membres:
        periodes = []
        for i in range(nb_echeances):
            mois_debut = i * mois_par_periode + 1
            mois_fin = mois_debut + mois_par_periode - 1
            debut = date(annee, mois_debut, 1)
            fin = date(annee, mois_fin, calendar.monthrange(annee, mois_fin)[1])

            montant_paye = db.session.query(
                func.coalesce(func.sum(Cotisation.montant), 0)
            ).filter(
                Cotisation.membre_id == m.id,
                Cotisation.statut == 'Paye',
                Cotisation.type_cotisation != 'Adhésion',
                Cotisation.date_paiement >= debut,
                Cotisation.date_paiement <= fin
            ).scalar()
            montant_paye = float(montant_paye or 0)

            periodes.append({
                'numero': i + 1,
                'montant_paye': montant_paye,
                'payee': montant_echeance > 0 and montant_paye >= montant_echeance,
            })

        total_attendu = montant_echeance * nb_echeances
        total_paye = sum(p['montant_paye'] for p in periodes)
        solde = round(total_paye - total_attendu, 2)  # négatif = doit de l'argent

        etat.append({
            'membre_id': m.id,
            'nom': m.nom,
            'prenom': m.prenom,
            'date_adhesion': m.date_adhesion,
            'periodes': periodes,
            'total_attendu': round(total_attendu, 2),
            'total_paye': round(total_paye, 2),
            'solde': solde,
            'statut': 'Pas à jour' if m.id in ids_en_retard else 'À jour',
        })

    return etat, nb_echeances

