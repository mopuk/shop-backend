"""add 'delivered' status to order status enum

Revision ID: 7af938794e10
Revises: ab666f0f5992
Create Date: 2026-10-12 19:20:10.176339

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "7af938794e10"
down_revision = "ab666f0f5992"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("DROP TYPE IF EXISTS orderstatus CASCADE")
    op.execute(
        "CREATE TYPE orderstatus AS ENUM ('processing', 'paid', 'canceled', 'created', 'failed', 'delivered')"
    )
    op.add_column(
        "orders",
        sa.Column(
            "status",
            sa.Enum(
                "processing",
                "paid",
                "canceled",
                "created",
                "failed",
                "delivered",
                name="orderstatus",
            ),
            nullable=False,
            server_default="processing",
        ),
    )


def downgrade():
    op.drop_column("orders", "status")
    op.execute("DROP TYPE IF EXISTS orderstatus")
    op.execute(
        "CREATE TYPE orderstatus AS ENUM ('processing', 'paid', 'canceled', 'created', 'failed')"
    )
    op.add_column(
        "orders",
        sa.Column(
            "status",
            sa.Enum(
                "processing",
                "paid",
                "canceled",
                "created",
                "failed",
                name="orderstatus",
            ),
            nullable=False,
            server_default="processing",
        ),
    )
