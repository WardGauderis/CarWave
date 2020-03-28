"""empty message

Revision ID: c29dfa00bb27
Revises: 50fc31115a21
Create Date: 2020-03-09 10:52:29.701710

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c29dfa00bb27'
down_revision = '50fc31115a21'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'email',
               existing_type=sa.VARCHAR(length=128),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'email',
               existing_type=sa.VARCHAR(length=128),
               nullable=True)
    # ### end Alembic commands ###
