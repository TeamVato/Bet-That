"""Add peer-to-peer betting tables only

Revision ID: 11edb756c09a
Revises:
Create Date: 2025-09-29 17:57:04.665540

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "11edb756c09a"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create peer_bets table
    op.create_table(
        "peer_bets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("bet_type", sa.String(length=50), nullable=False),
        sa.Column("creator_id", sa.Integer(), nullable=False),
        sa.Column("minimum_stake", sa.DECIMAL(precision=12, scale=2), nullable=False),
        sa.Column("maximum_stake", sa.DECIMAL(precision=12, scale=2), nullable=True),
        sa.Column("total_stake_pool", sa.DECIMAL(precision=12, scale=2), nullable=False),
        sa.Column("participant_limit", sa.Integer(), nullable=True),
        sa.Column("current_participants", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("starts_at", sa.DateTime(), nullable=True),
        sa.Column("locks_at", sa.DateTime(), nullable=True),
        sa.Column("resolves_at", sa.DateTime(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("is_public", sa.Boolean(), nullable=False),
        sa.Column("requires_approval", sa.Boolean(), nullable=False),
        sa.Column("auto_resolve", sa.Boolean(), nullable=False),
        sa.Column("possible_outcomes", sa.Text(), nullable=False),
        sa.Column("winning_outcome", sa.String(length=255), nullable=True),
        sa.Column("outcome_source", sa.Text(), nullable=True),
        sa.Column("platform_fee_percentage", sa.DECIMAL(precision=5, scale=2), nullable=False),
        sa.Column("creator_fee_percentage", sa.DECIMAL(precision=5, scale=2), nullable=False),
        sa.Column("tags", sa.Text(), nullable=True),
        sa.Column("external_reference", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["creator_id"],
            ["users.id"],
        ),
        sa.CheckConstraint("minimum_stake > 0", name="check_peer_bet_min_stake_positive"),
        sa.CheckConstraint(
            "maximum_stake IS NULL OR maximum_stake >= minimum_stake",
            name="check_peer_bet_max_stake_valid",
        ),
        sa.CheckConstraint(
            "participant_limit IS NULL OR participant_limit >= 2",
            name="check_peer_bet_participant_limit_valid",
        ),
        sa.CheckConstraint(
            "platform_fee_percentage >= 0 AND platform_fee_percentage <= 100",
            name="check_peer_bet_platform_fee_valid",
        ),
        sa.CheckConstraint(
            "creator_fee_percentage >= 0 AND creator_fee_percentage <= 100",
            name="check_peer_bet_creator_fee_valid",
        ),
        sa.CheckConstraint("total_stake_pool >= 0", name="check_peer_bet_total_stake_non_negative"),
        sa.CheckConstraint(
            "current_participants >= 0", name="check_peer_bet_current_participants_non_negative"
        ),
    )

    # Create indexes for peer_bets
    op.create_index("idx_peer_bets_creator_status", "peer_bets", ["creator_id", "status"])
    op.create_index("idx_peer_bets_category_status", "peer_bets", ["category", "status"])
    op.create_index("idx_peer_bets_public_active", "peer_bets", ["is_public", "status"])
    op.create_index("idx_peer_bets_locks_at", "peer_bets", ["locks_at"])
    op.create_index("idx_peer_bets_resolves_at", "peer_bets", ["resolves_at"])
    op.create_index("idx_peer_bets_deleted", "peer_bets", ["deleted_at"])
    op.create_index("ix_peer_bets_title", "peer_bets", ["title"])
    op.create_index("ix_peer_bets_category", "peer_bets", ["category"])
    op.create_index("ix_peer_bets_bet_type", "peer_bets", ["bet_type"])
    op.create_index("ix_peer_bets_creator_id", "peer_bets", ["creator_id"])
    op.create_index("ix_peer_bets_created_at", "peer_bets", ["created_at"])
    op.create_index("ix_peer_bets_starts_at", "peer_bets", ["starts_at"])
    op.create_index("ix_peer_bets_locks_at", "peer_bets", ["locks_at"])
    op.create_index("ix_peer_bets_resolves_at", "peer_bets", ["resolves_at"])
    op.create_index("ix_peer_bets_status", "peer_bets", ["status"])
    op.create_index("ix_peer_bets_is_public", "peer_bets", ["is_public"])

    # Create peer_bet_outcomes table
    op.create_table(
        "peer_bet_outcomes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("bet_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("odds", sa.DECIMAL(precision=8, scale=2), nullable=True),
        sa.Column("total_stakes", sa.DECIMAL(precision=12, scale=2), nullable=False),
        sa.Column("participant_count", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("probability", sa.DECIMAL(precision=6, scale=4), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["bet_id"],
            ["peer_bets.id"],
        ),
        sa.CheckConstraint("odds IS NULL OR odds >= 1.0", name="check_peer_bet_outcome_odds_valid"),
        sa.CheckConstraint(
            "probability IS NULL OR (probability >= 0.0 AND probability <= 1.0)",
            name="check_peer_bet_outcome_probability_valid",
        ),
        sa.CheckConstraint(
            "total_stakes >= 0", name="check_peer_bet_outcome_total_stakes_non_negative"
        ),
        sa.CheckConstraint(
            "participant_count >= 0", name="check_peer_bet_outcome_participant_count_non_negative"
        ),
    )

    # Create indexes for peer_bet_outcomes
    op.create_index("idx_peer_bet_outcomes_bet_status", "peer_bet_outcomes", ["bet_id", "status"])
    op.create_index("idx_peer_bet_outcomes_order", "peer_bet_outcomes", ["bet_id", "order_index"])
    op.create_index("ix_peer_bet_outcomes_bet_id", "peer_bet_outcomes", ["bet_id"])
    op.create_index("ix_peer_bet_outcomes_status", "peer_bet_outcomes", ["status"])

    # Create peer_bet_participants table
    op.create_table(
        "peer_bet_participants",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("bet_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("chosen_outcome", sa.String(length=255), nullable=False),
        sa.Column("stake_amount", sa.DECIMAL(precision=12, scale=2), nullable=False),
        sa.Column("potential_payout", sa.DECIMAL(precision=12, scale=2), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("joined_at", sa.DateTime(), nullable=False),
        sa.Column("withdrawn_at", sa.DateTime(), nullable=True),
        sa.Column("paid_out_at", sa.DateTime(), nullable=True),
        sa.Column("actual_payout", sa.DECIMAL(precision=12, scale=2), nullable=True),
        sa.Column("platform_fee", sa.DECIMAL(precision=12, scale=2), nullable=True),
        sa.Column("creator_fee", sa.DECIMAL(precision=12, scale=2), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["bet_id"],
            ["peer_bets.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.CheckConstraint("stake_amount > 0", name="check_peer_bet_participant_stake_positive"),
        sa.CheckConstraint(
            "potential_payout >= 0", name="check_peer_bet_participant_potential_payout_non_negative"
        ),
        sa.CheckConstraint(
            "actual_payout IS NULL OR actual_payout >= 0",
            name="check_peer_bet_participant_actual_payout_non_negative",
        ),
        sa.CheckConstraint(
            "platform_fee IS NULL OR platform_fee >= 0",
            name="check_peer_bet_participant_platform_fee_non_negative",
        ),
        sa.CheckConstraint(
            "creator_fee IS NULL OR creator_fee >= 0",
            name="check_peer_bet_participant_creator_fee_non_negative",
        ),
        sa.UniqueConstraint("bet_id", "user_id", name="unique_user_peer_bet_participation"),
    )

    # Create indexes for peer_bet_participants
    op.create_index(
        "idx_peer_bet_participants_user_status", "peer_bet_participants", ["user_id", "status"]
    )
    op.create_index(
        "idx_peer_bet_participants_bet_status", "peer_bet_participants", ["bet_id", "status"]
    )
    op.create_index("idx_peer_bet_participants_joined_at", "peer_bet_participants", ["joined_at"])
    op.create_index("ix_peer_bet_participants_bet_id", "peer_bet_participants", ["bet_id"])
    op.create_index("ix_peer_bet_participants_user_id", "peer_bet_participants", ["user_id"])
    op.create_index("ix_peer_bet_participants_status", "peer_bet_participants", ["status"])
    op.create_index("ix_peer_bet_participants_joined_at", "peer_bet_participants", ["joined_at"])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table("peer_bet_participants")
    op.drop_table("peer_bet_outcomes")
    op.drop_table("peer_bets")
