"""add valideur_id and valide_par_comptable to aides

Revision ID: aaaa_add_valideur_aides
Revises: zzzz_create_parametres_mutuelle
Create Date: 2026-07-08

"""
from alembic import op
import sqlalchemy as sa

revision = 'aaaa_add_valideur_aides'
down_revision = '8988b022e53d'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('aides', sa.Column('valideur_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_aides_valideur_id', 'aides', 'membres', ['valideur_id'], ['id']
    )
    op.add_column(
        'aides',
        sa.Column('valide_par_comptable', sa.Boolean(), nullable=False, server_default='false')
    )


def downgrade():
    op.drop_constraint('fk_aides_valideur_id', 'aides', type_='foreignkey')
    op.drop_column('aides', 'valideur_id')
    op.drop_column('aides', 'valide_par_comptable')
