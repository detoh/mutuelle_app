"""Conversion date_adhesion en type Date

Revision ID: 8988b022e53d
Revises: zzzz_create_parametres_mutuelle
Create Date: 2026-07-09
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '8988b022e53d'
down_revision = 'zzzz_create_parametres_mutuelle'
branch_labels = None
depends_on = None


def upgrade():
    # Conversion directe de date_adhesion en type DATE
    op.execute("""
        ALTER TABLE membres
        ALTER COLUMN date_adhesion TYPE DATE
        USING (
            CASE
                WHEN date_adhesion LIKE '%/%' THEN TO_DATE(date_adhesion, 'DD/MM/YYYY')
                ELSE date_adhesion::DATE
            END
        )
    """)


def downgrade():
    # Retour en type VARCHAR(50)
    op.execute("""
        ALTER TABLE membres
        ALTER COLUMN date_adhesion TYPE VARCHAR(50)
        USING date_adhesion::VARCHAR
    """)