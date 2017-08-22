"""empty message

Revision ID: 25a3261692e
Revises: None
Create Date: 2017-08-22 10:04:31.864465

"""

# revision identifiers, used by Alembic.
revision = '25a3261692e'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('lbc_entries',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('linkid', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('category', sa.String(), nullable=True),
    sa.Column('location', sa.String(), nullable=True),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.Column('price', sa.Integer(), nullable=True),
    sa.Column('imgurl', sa.String(), nullable=True),
    sa.Column('imgnumber', sa.Integer(), nullable=True),
    sa.Column('new', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('searches',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('terms', sa.String(), nullable=True),
    sa.Column('category', sa.Integer(), nullable=True),
    sa.Column('minprice', sa.Integer(), nullable=True),
    sa.Column('maxprice', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=20), nullable=True),
    sa.Column('password', sa.String(length=10), nullable=True),
    sa.Column('email', sa.String(length=50), nullable=True),
    sa.Column('registered_on', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_table('search_entry_links',
    sa.Column('search_id', sa.Integer(), nullable=True),
    sa.Column('lbc_entry_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['lbc_entry_id'], ['lbc_entries.id'], ),
    sa.ForeignKeyConstraint(['search_id'], ['searches.id'], )
    )
    op.create_table('search_user_links',
    sa.Column('search_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['search_id'], ['searches.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], )
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('search_user_links')
    op.drop_table('search_entry_links')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_table('searches')
    op.drop_table('lbc_entries')
    ### end Alembic commands ###
