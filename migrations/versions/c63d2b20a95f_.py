"""empty message

Revision ID: c63d2b20a95f
Revises: 
Create Date: 2020-04-02 15:00:17.331801

"""

from geoalchemy2.types import Geometry
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c63d2b20a95f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('cars',
    sa.Column('license_plate', sa.String(length=16), nullable=False),
    sa.Column('model', sa.String(length=128), nullable=False),
    sa.Column('colour', sa.String(length=32), nullable=False),
    sa.Column('passenger_places', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('license_plate')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=False),
    sa.Column('first_name', sa.String(length=64), nullable=False),
    sa.Column('last_name', sa.String(length=64), nullable=False),
    sa.Column('email', sa.String(length=128), nullable=True),
    sa.Column('phone_number', sa.String(length=32), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_table('drivers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('rating', sa.Numeric(precision=2, scale=1), nullable=True),
    sa.Column('num_ratings', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('passengers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('rating', sa.Numeric(precision=2, scale=1), nullable=True),
    sa.Column('num_ratings', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('car_links',
    sa.Column('driver_id', sa.Integer(), nullable=False),
    sa.Column('car_license_plate', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['car_license_plate'], ['cars.license_plate'], ),
    sa.ForeignKeyConstraint(['driver_id'], ['drivers.id'], ),
    sa.PrimaryKeyConstraint('driver_id', 'car_license_plate')
    )
    op.create_table('rides',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('driver_id', sa.Integer(), nullable=False),
    sa.Column('passenger_places', sa.Integer(), nullable=False),
    sa.Column('request_time', sa.DateTime(), nullable=False),
    sa.Column('departure_time', sa.DateTime(), nullable=True),
    sa.Column('departure_address', Geometry(geometry_type='POINT', srid=4326), nullable=False),
    sa.Column('arrival_time', sa.DateTime(), nullable=False),
    sa.Column('arrival_address', Geometry(geometry_type='POINT', srid=4326), nullable=False),
    sa.ForeignKeyConstraint(['driver_id'], ['drivers.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('passenger_requests',
    sa.Column('ride_id', sa.Integer(), nullable=False),
    sa.Column('passenger_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum('accepted', 'pending', 'declined', name='status_enum'), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('last_modified', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['passenger_id'], ['passengers.id'], ),
    sa.ForeignKeyConstraint(['ride_id'], ['rides.id'], ),
    sa.PrimaryKeyConstraint('ride_id', 'passenger_id')
    )
    op.create_table('ride_links',
    sa.Column('ride_id', sa.Integer(), nullable=False),
    sa.Column('passenger_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['passenger_id'], ['passengers.id'], ),
    sa.ForeignKeyConstraint(['ride_id'], ['rides.id'], ),
    sa.PrimaryKeyConstraint('ride_id', 'passenger_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ride_links')
    op.drop_table('passenger_requests')
    op.drop_table('rides')
    op.drop_table('car_links')
    op.drop_table('passengers')
    op.drop_table('drivers')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_table('users')
    op.drop_table('cars')
    # ### end Alembic commands ###
