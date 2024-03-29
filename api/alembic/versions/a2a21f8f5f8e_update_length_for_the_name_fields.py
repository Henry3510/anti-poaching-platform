"""update length for the name fields

Revision ID: a2a21f8f5f8e
Revises: d12cd1dbac38
Create Date: 2022-01-09 04:31:24.649879

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "a2a21f8f5f8e"
down_revision = "d12cd1dbac38"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "taxon_class",
        "name",
        existing_type=sa.VARCHAR(length=12),
        type_=sa.String(length=255),
        existing_nullable=False,
    )
    op.alter_column(
        "taxon_family",
        "name",
        existing_type=sa.VARCHAR(length=12),
        type_=sa.String(length=255),
        existing_nullable=False,
    )
    op.alter_column(
        "taxon_genus",
        "name",
        existing_type=sa.VARCHAR(length=12),
        type_=sa.String(length=255),
        existing_nullable=False,
    )
    op.alter_column(
        "taxon_order",
        "name",
        existing_type=sa.VARCHAR(length=12),
        type_=sa.String(length=255),
        existing_nullable=False,
    )
    op.alter_column(
        "taxon_species",
        "name",
        existing_type=sa.VARCHAR(length=12),
        type_=sa.String(length=255),
        existing_nullable=False,
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "taxon_species",
        "name",
        existing_type=sa.String(length=255),
        type_=sa.VARCHAR(length=12),
        existing_nullable=False,
    )
    op.alter_column(
        "taxon_order",
        "name",
        existing_type=sa.String(length=255),
        type_=sa.VARCHAR(length=12),
        existing_nullable=False,
    )
    op.alter_column(
        "taxon_genus",
        "name",
        existing_type=sa.String(length=255),
        type_=sa.VARCHAR(length=12),
        existing_nullable=False,
    )
    op.alter_column(
        "taxon_family",
        "name",
        existing_type=sa.String(length=255),
        type_=sa.VARCHAR(length=12),
        existing_nullable=False,
    )
    op.alter_column(
        "taxon_class",
        "name",
        existing_type=sa.String(length=255),
        type_=sa.VARCHAR(length=12),
        existing_nullable=False,
    )
    # ### end Alembic commands ###
