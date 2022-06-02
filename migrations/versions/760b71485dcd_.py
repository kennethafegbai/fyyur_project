"""empty message

Revision ID: 760b71485dcd
Revises: 623efe22c3d0
Create Date: 2022-05-31 17:37:28.310440

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '760b71485dcd'
down_revision = '623efe22c3d0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artists', sa.Column('website_link', sa.String(length=120), nullable=True))
    op.drop_column('artists', 'website')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artists', sa.Column('website', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.drop_column('artists', 'website_link')
    # ### end Alembic commands ###