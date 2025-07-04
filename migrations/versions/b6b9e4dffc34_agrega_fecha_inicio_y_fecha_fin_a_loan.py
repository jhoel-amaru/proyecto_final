"""Agrega fecha_inicio y fecha_fin a Loan

Revision ID: b6b9e4dffc34
Revises: 
Create Date: 2025-06-23 17:59:26.925486

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b6b9e4dffc34'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('loan', schema=None) as batch_op:
        batch_op.add_column(sa.Column('fecha_inicio', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('fecha_fin', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('loan', schema=None) as batch_op:
        batch_op.drop_column('fecha_fin')
        batch_op.drop_column('fecha_inicio')

    # ### end Alembic commands ###
