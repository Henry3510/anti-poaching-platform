"""Add defendant table

Revision ID: 17cc2fc38779
Revises: b736b7d54146
Create Date: 2022-02-19 17:47:47.387224

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "17cc2fc38779"
down_revision = "b736b7d54146"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "defendant",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("gender", sa.String(length=1), nullable=True),
        sa.Column("birth", sa.Date(), nullable=True),
        sa.Column("education_level", sa.String(length=20), nullable=True),
        sa.Column("judgment_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["judgment_id"],
            ["judgment.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("defendant")
    # ### end Alembic commands ###