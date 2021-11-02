"""init

Revision ID: 131bec8bfe90
Revises:
Create Date: 2021-10-31 22:29:17.924974

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "131bec8bfe90"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "companies",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "employees",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("birthday", sa.Date(), nullable=True),
        sa.Column("salary", sa.Numeric(), nullable=True),
        sa.Column("shares_owned", sa.Integer(), nullable=True),
        sa.Column("company_id", postgresql.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )


def downgrade():
    op.drop_table("employees")
    op.drop_table("companies")
