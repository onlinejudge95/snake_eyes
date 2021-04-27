import sqlalchemy as sa

from alembic import op

from lib.src.util_datetime import tz_aware_datetime
from lib.src.util_sqlalchemy import AwareDateTime


"""
Initial migration

Revision ID: 001
Revises: 
Create Date: 2021-04-23 16:49:52.730848
"""

# revision identifiers, used by Alembic.
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "coupons",
        sa.Column("created_on", AwareDateTime(timezone=True), nullable=True),
        sa.Column("updated_on", AwareDateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=128), nullable=True),
        sa.Column(
            "duration",
            sa.Enum("forever", "once", "repeating", name="duration_types"),
            server_default="forever",
            nullable=False,
        ),
        sa.Column("amount_off", sa.Integer(), nullable=True),
        sa.Column("percent_off", sa.Integer(), nullable=True),
        sa.Column("currency", sa.String(length=8), nullable=True),
        sa.Column("duration_in_months", sa.Integer(), nullable=True),
        sa.Column("max_redemptions", sa.Integer(), nullable=True),
        sa.Column("redeem_by", AwareDateTime(timezone=True), nullable=True),
        sa.Column("times_redeemed", sa.Integer(), nullable=False),
        sa.Column("valid", sa.Boolean(), server_default="1", nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_coupons_code"), "coupons", ["code"], unique=True)
    op.create_index(op.f("ix_coupons_duration"), "coupons", ["duration"], unique=False)
    op.create_index(
        op.f("ix_coupons_max_redemptions"), "coupons", ["max_redemptions"], unique=False
    )
    op.create_index(
        op.f("ix_coupons_redeem_by"), "coupons", ["redeem_by"], unique=False
    )
    op.create_index(
        op.f("ix_coupons_times_redeemed"), "coupons", ["times_redeemed"], unique=False
    )
    op.create_table(
        "users",
        sa.Column("created_on", AwareDateTime(timezone=True), nullable=True),
        sa.Column("updated_on", AwareDateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "role",
            sa.Enum("member", "admin", name="role_types", native_enum=False),
            server_default="member",
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), server_default="1", nullable=False),
        sa.Column("username", sa.String(length=24), nullable=True),
        sa.Column("email", sa.String(length=255), server_default="", nullable=False),
        sa.Column("password", sa.String(length=128), server_default="", nullable=False),
        sa.Column("name", sa.String(length=128), nullable=True),
        sa.Column("payment_id", sa.String(length=128), nullable=True),
        sa.Column(
            "cancelled_subscription_on", AwareDateTime(timezone=True), nullable=True
        ),
        sa.Column("previous_plan", sa.String(length=128), nullable=True),
        sa.Column("coins", sa.BigInteger(), nullable=True),
        sa.Column("last_bet_on", AwareDateTime(timezone=True), nullable=True),
        sa.Column("sign_in_count", sa.Integer(), nullable=False),
        sa.Column("current_sign_in_on", AwareDateTime(timezone=True), nullable=True),
        sa.Column("current_sign_in_ip", sa.String(length=45), nullable=True),
        sa.Column("last_sign_in_on", AwareDateTime(timezone=True), nullable=True),
        sa.Column("last_sign_in_ip", sa.String(length=45), nullable=True),
        sa.Column("locale", sa.String(length=5), server_default="en", nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_name"), "users", ["name"], unique=False)
    op.create_index(op.f("ix_users_payment_id"), "users", ["payment_id"], unique=False)
    op.create_index(op.f("ix_users_role"), "users", ["role"], unique=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)
    op.create_table(
        "bets",
        sa.Column("created_on", AwareDateTime(timezone=True), nullable=True),
        sa.Column("updated_on", AwareDateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("guess", sa.Integer(), nullable=True),
        sa.Column("dice_1", sa.Integer(), nullable=True),
        sa.Column("dice_2", sa.Integer(), nullable=True),
        sa.Column("roll", sa.Integer(), nullable=True),
        sa.Column("wagered", sa.BigInteger(), nullable=True),
        sa.Column("payout", sa.Float(), nullable=True),
        sa.Column("net", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], onupdate="CASCADE", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_bets_user_id"), "bets", ["user_id"], unique=False)
    op.create_table(
        "credit_cards",
        sa.Column("created_on", AwareDateTime(timezone=True), nullable=True),
        sa.Column("updated_on", AwareDateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("brand", sa.String(length=32), nullable=True),
        sa.Column("last4", sa.Integer(), nullable=True),
        sa.Column("exp_date", sa.Date(), nullable=True),
        sa.Column("is_expiring", sa.Boolean(), server_default="0", nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], onupdate="CASCADE", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_credit_cards_exp_date"), "credit_cards", ["exp_date"], unique=False
    )
    op.create_index(
        op.f("ix_credit_cards_user_id"), "credit_cards", ["user_id"], unique=False
    )
    op.create_table(
        "invoices",
        sa.Column("created_on", AwareDateTime(timezone=True), nullable=True),
        sa.Column("updated_on", AwareDateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("plan", sa.String(length=128), nullable=True),
        sa.Column("receipt_number", sa.String(length=128), nullable=True),
        sa.Column("description", sa.String(length=128), nullable=True),
        sa.Column("period_start_on", sa.Date(), nullable=True),
        sa.Column("period_end_on", sa.Date(), nullable=True),
        sa.Column("currency", sa.String(length=8), nullable=True),
        sa.Column("tax", sa.Integer(), nullable=True),
        sa.Column("tax_percent", sa.Float(), nullable=True),
        sa.Column("total", sa.Integer(), nullable=True),
        sa.Column("brand", sa.String(length=32), nullable=True),
        sa.Column("last4", sa.Integer(), nullable=True),
        sa.Column("exp_date", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], onupdate="CASCADE", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_invoices_exp_date"), "invoices", ["exp_date"], unique=False
    )
    op.create_index(op.f("ix_invoices_plan"), "invoices", ["plan"], unique=False)
    op.create_index(
        op.f("ix_invoices_receipt_number"), "invoices", ["receipt_number"], unique=False
    )
    op.create_index(op.f("ix_invoices_user_id"), "invoices", ["user_id"], unique=False)
    op.create_table(
        "subscriptions",
        sa.Column("created_on", AwareDateTime(timezone=True), nullable=True),
        sa.Column("updated_on", AwareDateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("plan", sa.String(length=128), nullable=True),
        sa.Column("coupon", sa.String(length=128), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], onupdate="CASCADE", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_subscriptions_user_id"), "subscriptions", ["user_id"], unique=False
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_subscriptions_user_id"), table_name="subscriptions")
    op.drop_table("subscriptions")
    op.drop_index(op.f("ix_invoices_user_id"), table_name="invoices")
    op.drop_index(op.f("ix_invoices_receipt_number"), table_name="invoices")
    op.drop_index(op.f("ix_invoices_plan"), table_name="invoices")
    op.drop_index(op.f("ix_invoices_exp_date"), table_name="invoices")
    op.drop_table("invoices")
    op.drop_index(op.f("ix_credit_cards_user_id"), table_name="credit_cards")
    op.drop_index(op.f("ix_credit_cards_exp_date"), table_name="credit_cards")
    op.drop_table("credit_cards")
    op.drop_index(op.f("ix_bets_user_id"), table_name="bets")
    op.drop_table("bets")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_role"), table_name="users")
    op.drop_index(op.f("ix_users_payment_id"), table_name="users")
    op.drop_index(op.f("ix_users_name"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_coupons_times_redeemed"), table_name="coupons")
    op.drop_index(op.f("ix_coupons_redeem_by"), table_name="coupons")
    op.drop_index(op.f("ix_coupons_max_redemptions"), table_name="coupons")
    op.drop_index(op.f("ix_coupons_duration"), table_name="coupons")
    op.drop_index(op.f("ix_coupons_code"), table_name="coupons")
    op.drop_table("coupons")
    ### end Alembic commands ###
