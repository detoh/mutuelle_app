"""fix sp_creer_membre to explicitly set statut='Actif'

Revision ID: yyyy_fix_sp_creer_membre_statut
Revises: xxxx_fix_statut_default
Create Date: 2026-07-03

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'yyyy_fix_sp_creer_membre_statut'
down_revision = 'xxxx_fix_statut_default'
branch_labels = None
depends_on = None


# Définition ORIGINALE de la procédure (pour le downgrade)
OLD_PROCEDURE = """
CREATE OR REPLACE PROCEDURE public.sp_creer_membre(
    IN p_nom character varying,
    IN p_prenom character varying,
    IN p_email character varying,
    IN p_telephone character varying,
    IN p_fonction character varying,
    IN p_service character varying,
    IN p_emploi character varying,
    IN p_date_adhesion character varying,
    IN p_password_hash character varying,
    IN p_is_admin boolean DEFAULT false
)
LANGUAGE plpgsql
AS $procedure$
BEGIN
    IF EXISTS (SELECT 1 FROM membres WHERE email = p_email) THEN
        RAISE EXCEPTION 'EMAIL_DEJA_UTILISE: %', p_email;
    END IF;
    INSERT INTO membres (nom, prenom, email, telephone, fonction, service,
                         emploi, date_adhesion, password_hash, is_admin)
    VALUES (p_nom, p_prenom, p_email, p_telephone, p_fonction, p_service,
            p_emploi, p_date_adhesion, p_password_hash, p_is_admin);
END;
$procedure$;
"""

# Nouvelle définition : signature identique, statut='Actif' ajouté à l'INSERT
NEW_PROCEDURE = """
CREATE OR REPLACE PROCEDURE public.sp_creer_membre(
    IN p_nom character varying,
    IN p_prenom character varying,
    IN p_email character varying,
    IN p_telephone character varying,
    IN p_fonction character varying,
    IN p_service character varying,
    IN p_emploi character varying,
    IN p_date_adhesion character varying,
    IN p_password_hash character varying,
    IN p_is_admin boolean DEFAULT false
)
LANGUAGE plpgsql
AS $procedure$
BEGIN
    IF EXISTS (SELECT 1 FROM membres WHERE email = p_email) THEN
        RAISE EXCEPTION 'EMAIL_DEJA_UTILISE: %', p_email;
    END IF;
    INSERT INTO membres (nom, prenom, email, telephone, fonction, service,
                         emploi, date_adhesion, password_hash, is_admin,
                         statut)
    VALUES (p_nom, p_prenom, p_email, p_telephone, p_fonction, p_service,
            p_emploi, p_date_adhesion, p_password_hash, p_is_admin,
            'Actif');
END;
$procedure$;
"""


def upgrade():
    op.execute(NEW_PROCEDURE)


def downgrade():
    op.execute(OLD_PROCEDURE)
