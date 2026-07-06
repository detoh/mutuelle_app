"""fix statut default to 'Actif'

Revision ID: xxxx_fix_statut_default
Revises: <mets_ici_l_id_de_ta_derniere_revision>
Create Date: 2026-07-03

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'xxxx_fix_statut_default'
down_revision = 'b7dbc79eb504'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Ajoute un DEFAULT au niveau de la base pour la colonne statut.
    #    Filet de sécurité : s'applique même si un INSERT (procédure stockée,
    #    script SQL brut, etc.) omet la colonne.
    op.execute("""
        ALTER TABLE membres
        ALTER COLUMN statut SET DEFAULT 'Actif';
    """)

    # 2. Corrige les membres déjà importés dont le statut est NULL ou vide,
    #    conséquence du bug (INSERT sans la colonne statut, donc pas de
    #    DEFAULT appliqué avant cette migration).
    op.execute("""
        UPDATE membres
        SET statut = 'Actif'
        WHERE statut IS NULL OR statut = '';
    """)


def downgrade():
    # Retire le DEFAULT ajouté. On ne revient pas sur les données déjà
    # corrigées (on ne sait pas distinguer un statut légitimement 'Actif'
    # de celui corrigé par cette migration).
    op.execute("""
        ALTER TABLE membres
        ALTER COLUMN statut DROP DEFAULT;
    """)
