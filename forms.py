from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SelectField, RadioField, FloatField, DateField, DecimalField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange, EqualTo


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    remember = BooleanField('Se souvenir de moi')
    submit = SubmitField('Se connecter')

class ChangerMotDePasseForm(FlaskForm):
    nouveau_mot_de_passe = PasswordField(
        'Nouveau mot de passe',
        validators=[DataRequired(), Length(min=8, message="8 caractères minimum")]
    )
    confirmation = PasswordField(
        'Confirmer le mot de passe',
        validators=[DataRequired(), EqualTo('nouveau_mot_de_passe', message="Les mots de passe ne correspondent pas")]
    )
    submit = SubmitField('Changer mon mot de passe')
    
class RegisterForm(FlaskForm):
    nom = StringField('Nom', validators=[DataRequired(), Length(max=100)])
    prenom = StringField('Prénom', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    telephone = StringField('Téléphone', validators=[Optional(), Length(max=20)])
    fonction = StringField('Fonction', validators=[Optional(), Length(max=100)])
    service = StringField('Service', validators=[Optional(), Length(max=100)])
    emploi = StringField('Emploi', validators=[Optional(), Length(max=100)])
    password = PasswordField('Mot de passe', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmer mot de passe', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Créer le compte')

class CotisationForm(FlaskForm):
    membre_id = SelectField('Membre', coerce=int, validators=[DataRequired()])
    type_cotisation = SelectField('Type', choices=[('Mensuelle', 'Mensuelle'),('Adhésion', 'Adhésion'), ('Annuelle', 'Annuelle'),('Semestrielle', 'Semestrielle'),('Trimestrielle', 'Trimestrielle'), ('Exceptionnelle', 'Exceptionnelle')], validators=[DataRequired()])
    montant = DecimalField('Montant (FCFA)', validators=[DataRequired(), NumberRange(min=0)])
    date_paiement = DateField('Date de paiement', validators=[DataRequired()])
    submit = SubmitField('Enregistrer')

class AideForm(FlaskForm):
    membre_id = SelectField('Membre', coerce=int, validators=[DataRequired()])
    type_aide = SelectField('Type d\'aide', choices=[('Medical', 'Medical'), ('Social', 'Social'), ('Scolarité', 'Scolarité'), ('Autre', 'Autre')], validators=[DataRequired()])
    montant = DecimalField('Montant (FCFA)', validators=[DataRequired(), NumberRange(min=0)])
    #date_aide = DateField('Date de l\'aide', validators=[DataRequired()])
    date_attribution = DateField('Date de l\'aide', format='%Y-%m-%d', validators=[DataRequired()])
    description = TextAreaField('Description / Motif', validators=[DataRequired()])
    submit = SubmitField('Accorder l\'aide')

class EvenementForm(FlaskForm):
    nom = StringField('Nom de l\'événement', validators=[DataRequired()])
    budget_prevu = FloatField('Budget prévu', validators=[DataRequired()])
    depenses_reelles = FloatField('Dépenses réelles', validators=[Optional()], default=0.0)
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()]) # Ajustez le format selon votre besoin
    description = TextAreaField('Description', validators=[Optional()])
    statut = BooleanField('Événement Actif / Confirmé', default=True)
    submit = SubmitField('Enregistrer')

class ProjetForm(FlaskForm):
    titreprojet = StringField('Titre du projet', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[Optional()])
    datedebut = DateField('Date de début', validators=[DataRequired()])
    datefiprojet = DateField('Date de fin', validators=[Optional()])
    coutexecution = DecimalField('Coût d\'exécution (FCFA)', validators=[Optional(), NumberRange(min=0)])
    nomdonateur = StringField('Nom du donateur', validators=[Optional(), Length(max=200)])
    statut = SelectField('Statut', choices=[('En cours', 'En cours'), ('Terminé', 'Terminé'), ('Reporté', 'Reporté'), ('Annulé', 'Annulé')], validators=[DataRequired()])
    submit = SubmitField('Créer le projet')

class AjoutMembreFamilleForm(FlaskForm):
    """Formulaire pour ajouter un membre de la famille"""
    nom = StringField('Nom', validators=[DataRequired(message="Le nom est obligatoire")])
    prenom = StringField('Prénom', validators=[DataRequired(message="Le prénom est obligatoire")])
    lien_parente = SelectField('Lien de parenté', choices=[
        ('', '-- Sélectionner --'),
        ('Conjoint', 'Conjoint(e)'),
        ('Enfant', 'Enfant'),
        ('Père', 'Père'),
        ('Mère', 'Mère'),
        ('Frère', 'Frère'),
        ('Sœur', 'Sœur'),
        ('Autre', 'Autre')
    ], validators=[DataRequired(message="Le lien de parenté est obligatoire")])
    date_naissance = DateField('Date de naissance', validators=[DataRequired(message="La date de naissance est obligatoire")])
    telephone = StringField('Téléphone', validators=[Optional(), Length(max=20)])
    adresse = TextAreaField('Adresse', validators=[Optional()])
    est_a_charge = BooleanField('Personne à charge')
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Ajouter le membre')

class DeclarationEvenementForm(FlaskForm):
    """Formulaire pour déclarer un événement familial"""
    type_evenement = RadioField('Type d\'événement', choices=[
        ('Deces', 'Décès'),
        ('Naissance', 'Naissance'),
        ('Mariage', 'Mariage'),
        ('Maladie', 'Maladie'),
        ('Accident', 'Accident'),
        ('Retraite', 'Retraite'),
        ('Mutation', 'Mutation'),
        ('Autres', 'Autres')
    ], default='Deces', validators=[DataRequired(message="Le type d'événement est obligatoire")])
    # Membre de la famille concerné (utile pour Décès / Naissance). Le choices
    # réel est injecté dynamiquement dans la vue Flask via form.famille_id.choices = [...]
    # car la liste dépend du membre connecté.
    famille_id = SelectField('Membre de la famille concerné', coerce=int, validators=[Optional()])
    date_evenement = DateField('Date de l\'événement', validators=[DataRequired(message="La date est obligatoire")])
    description = TextAreaField('Description détaillée', validators=[Optional(), Length(max=500)])
    montant_demande = DecimalField('Montant d\'aide sollicité (FCFA)', validators=[Optional(), NumberRange(min=0)])
    piece_justificative = FileField('Pièce justificative', validators=[
        Optional(),
        FileAllowed(['pdf', 'jpg', 'jpeg', 'png'], 'Seuls les fichiers PDF, JPG, PNG sont autorisés.')
    ])
    notes = TextAreaField('Notes / Commentaires', validators=[Optional()])
    submit = SubmitField('Déclarer l\'événement')

class ParametresMutuelleForm(FlaskForm):
    frequence_cotisation = SelectField(
        'Fréquence de cotisation',
        choices=[
            ('mensuelle', 'Mensuelle (12 fois/an)'),
            ('trimestrielle', 'Trimestrielle (4 fois/an)'),
            ('semestrielle', 'Semestrielle (2 fois/an)'),
        ],
        validators=[DataRequired()]
    )
    montant_cotisation_annuel = DecimalField(
        'Montant de cotisation annuel (FCFA)',
        validators=[DataRequired(), NumberRange(min=0)]
    )
    submit = SubmitField('Enregistrer') 

class ContactForm(FlaskForm):
    nom = StringField('Nom complet', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    telephone = StringField('Téléphone', validators=[Optional(), Length(max=20)])
    sujet = StringField('Sujet', validators=[DataRequired(), Length(max=150)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(max=2000)]
    )
    submit = SubmitField('Envoyer')    