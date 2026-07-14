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
    # Remplace ton ancien op.execute par celui-ci :
    op.execute("""
        ALTER TABLE membres
        ALTER COLUMN date_adhesion TYPE DATE
        USING (
            CASE
                WHEN date_adhesion::text LIKE '%/%' THEN TO_DATE(date_adhesion::text, 'DD/MM/YYYY')
                ELSE date_adhesion::text::DATE
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