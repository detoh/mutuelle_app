"""create parametres_mutuelle table (frequence de cotisation)

Revision ID: zzzz_create_parametres_mutuelle
Revises: yyyy_fix_sp_creer_membre_statut
Create Date: 2026-07-03

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'zzzz_create_parametres_mutuelle'
down_revision = 'yyyy_fix_sp_creer_membre_statut'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'parametres_mutuelle',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column(
            'frequence_cotisation', sa.String(length=20),
            nullable=False, server_default='mensuelle'
        ),
        sa.Column(
            'montant_cotisation_annuel', sa.Numeric(10, 2),
            nullable=False, server_default='0'
        ),
        # Empêche d'avoir plusieurs lignes (table singleton) : seule id=1
        # est autorisée.
        sa.CheckConstraint('id = 1', name='ck_parametres_mutuelle_singleton'),
        sa.CheckConstraint(
            "frequence_cotisation IN ('mensuelle', 'trimestrielle', 'semestrielle')",
            name='ck_parametres_mutuelle_frequence_valide'
        ),
    )

    # Insère la ligne unique par défaut.
    op.execute("""
        INSERT INTO parametres_mutuelle (id, frequence_cotisation, montant_cotisation_annuel)
        VALUES (1, 'mensuelle', 0);
    """)


def downgrade():
    op.drop_table('parametres_mutuelle')
