"""empty message

Revision ID: a441187911a2
Revises: 
Create Date: 2020-02-26 18:31:58.156444

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a441187911a2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('adresses',
    sa.Column('adress_id', sa.Integer(), nullable=False),
    sa.Column('adress_name', sa.VARCHAR(), nullable=False),
    sa.PrimaryKeyConstraint('adress_id')
    )
    op.create_table('cars',
    sa.Column('license_plate', sa.VARCHAR(), nullable=False),
    sa.Column('model', sa.VARCHAR(), nullable=False),
    sa.Column('color', sa.VARCHAR(), nullable=False),
    sa.Column('num_passengers', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('license_plate')
    )
    op.create_table('drivers',
    sa.Column('driver_id', sa.Integer(), nullable=False),
    sa.Column('rating', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('driver_id')
    )
    op.create_table('passengers',
    sa.Column('passenger_id', sa.Integer(), nullable=False),
    sa.Column('rating', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('passenger_id')
    )
    op.create_table('car_links',
    sa.Column('driver_id', sa.Integer(), nullable=False),
    sa.Column('license_plate', sa.VARCHAR(), nullable=False),
    sa.ForeignKeyConstraint(['driver_id'], ['drivers.driver_id'], ),
    sa.ForeignKeyConstraint(['license_plate'], ['cars.license_plate'], ),
    sa.PrimaryKeyConstraint('driver_id', 'license_plate')
    )
    op.create_table('rides',
    sa.Column('ride_id', sa.Integer(), nullable=False),
    sa.Column('driver_id', sa.Integer(), nullable=True),
    sa.Column('passenger_id', sa.Integer(), nullable=False),
    sa.Column('request_time', sa.TIMESTAMP(), nullable=False),
    sa.Column('departure_time', sa.TIMESTAMP(), nullable=True),
    sa.Column('arrival_time', sa.TIMESTAMP(), nullable=True),
    sa.Column('departure_adress_id', sa.Integer(), nullable=False),
    sa.Column('arrival_adress_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['arrival_adress_id'], ['adresses.adress_id'], ),
    sa.ForeignKeyConstraint(['departure_adress_id'], ['adresses.adress_id'], ),
    sa.ForeignKeyConstraint(['driver_id'], ['drivers.driver_id'], ),
    sa.ForeignKeyConstraint(['passenger_id'], ['passengers.passenger_id'], ),
    sa.PrimaryKeyConstraint('ride_id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('first_name', sa.VARCHAR(), nullable=False),
    sa.Column('last_name', sa.VARCHAR(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
    sa.Column('home_adress_id', sa.Integer(), nullable=True),
    sa.Column('phone_number', sa.Integer(), nullable=True),
    sa.Column('email_adress', sa.String(length=128), nullable=True),
    sa.ForeignKeyConstraint(['home_adress_id'], ['adresses.adress_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_table('user')
    op.drop_table('rides')
    op.drop_table('car_links')
    op.drop_table('passengers')
    op.drop_table('drivers')
    op.drop_table('cars')
    op.drop_table('adresses')
    # ### end Alembic commands ###
