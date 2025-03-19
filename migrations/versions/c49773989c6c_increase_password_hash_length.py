"""increase password_hash length

Revision ID: c49773989c6c
Revises: 
Create Date: 2025-03-19 14:38:45.338857

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'c49773989c6c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password_hash',
               existing_type=mysql.VARCHAR(collation='utf8mb3_bin', length=128),
               type_=sa.String(length=255),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password_hash',
               existing_type=sa.String(length=255),
               type_=mysql.VARCHAR(collation='utf8mb3_bin', length=128),
               nullable=True)

    # ### end Alembic commands ###
