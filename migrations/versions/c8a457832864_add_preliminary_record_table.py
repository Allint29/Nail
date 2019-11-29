"""add preliminary_record table

Revision ID: c8a457832864
Revises: ea8ca5d09dec
Create Date: 2019-11-23 08:31:35.953848

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c8a457832864'
down_revision = 'ea8ca5d09dec'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('preliminary_record',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name_of_client', sa.String(), nullable=True),
    sa.Column('phone_of_client', sa.Integer(), nullable=True),
    sa.Column('message_of_client', sa.String(), nullable=True),
    sa.Column('message_worked', sa.Integer(), nullable=True),
    sa.Column('time_to_record', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('preliminary_record')
    # ### end Alembic commands ###