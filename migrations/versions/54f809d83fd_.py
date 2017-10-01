"""empty message

Revision ID: 54f809d83fd
Revises: 1f47fba1006
Create Date: 2017-10-01 18:15:30.385275

"""

# revision identifiers, used by Alembic.
revision = '54f809d83fd'
down_revision = '1f47fba1006'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('searches', sa.Column('zipcode', sa.String(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('searches', 'zipcode')
    ### end Alembic commands ###
