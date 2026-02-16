"""Initial schema — all 7 tables.

Revision ID: 001
Revises:
Create Date: 2026-02-16
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Companies
    op.create_table(
        "companies",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("ticker", sa.String(10), unique=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("exchange", sa.String(10), nullable=False),
        sa.Column("sector", sa.String(100), nullable=False),
        sa.Column("industry", sa.String(100), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("cik", sa.String(20), nullable=True),
        sa.Column("sedar_id", sa.String(20), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_companies_ticker", "companies", ["ticker"], unique=True)
    op.create_index("ix_companies_exchange_sector", "companies", ["exchange", "sector"])

    # Financial Snapshots
    op.create_table(
        "financial_snapshots",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("company_id", UUID(as_uuid=True), sa.ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("fiscal_year", sa.Integer(), nullable=False),
        sa.Column("fiscal_quarter", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        # Income statement
        sa.Column("revenue", sa.Numeric(20, 2)),
        sa.Column("cost_of_revenue", sa.Numeric(20, 2)),
        sa.Column("gross_profit", sa.Numeric(20, 2)),
        sa.Column("operating_income", sa.Numeric(20, 2)),
        sa.Column("net_income", sa.Numeric(20, 2)),
        sa.Column("ebitda", sa.Numeric(20, 2)),
        sa.Column("eps_diluted", sa.Numeric(12, 4)),
        sa.Column("shares_outstanding", sa.Numeric(16, 0)),
        # Balance sheet
        sa.Column("total_assets", sa.Numeric(20, 2)),
        sa.Column("total_liabilities", sa.Numeric(20, 2)),
        sa.Column("total_equity", sa.Numeric(20, 2)),
        sa.Column("cash_and_equivalents", sa.Numeric(20, 2)),
        sa.Column("total_debt", sa.Numeric(20, 2)),
        # Cash flow
        sa.Column("operating_cash_flow", sa.Numeric(20, 2)),
        sa.Column("capital_expenditures", sa.Numeric(20, 2)),
        sa.Column("free_cash_flow", sa.Numeric(20, 2)),
        # Margins & ratios
        sa.Column("gross_margin", sa.Numeric(8, 4)),
        sa.Column("operating_margin", sa.Numeric(8, 4)),
        sa.Column("net_margin", sa.Numeric(8, 4)),
        sa.Column("roe", sa.Numeric(8, 4)),
        sa.Column("debt_to_equity", sa.Numeric(8, 4)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_snapshots_company_period", "financial_snapshots", ["company_id", "fiscal_year", "fiscal_quarter"], unique=True)

    # Segments
    op.create_table(
        "segments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("snapshot_id", UUID(as_uuid=True), sa.ForeignKey("financial_snapshots.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("revenue", sa.Numeric(20, 2)),
        sa.Column("operating_income", sa.Numeric(20, 2)),
        sa.Column("revenue_pct", sa.Numeric(8, 4)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Business Profiles
    op.create_table(
        "business_profiles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("company_id", UUID(as_uuid=True), sa.ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("business_model", sa.Text(), nullable=False),
        sa.Column("competitive_position", sa.Text(), nullable=False),
        sa.Column("key_products", sa.Text(), nullable=False),
        sa.Column("geographic_mix", sa.Text(), nullable=False),
        sa.Column("moat_assessment", sa.String(50), nullable=False),
        sa.Column("moat_sources", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Thesis Versions
    op.create_table(
        "thesis_versions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("company_id", UUID(as_uuid=True), sa.ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("snapshot_id", UUID(as_uuid=True), sa.ForeignKey("financial_snapshots.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        # Three scenarios
        sa.Column("bull_case", sa.Text(), nullable=False),
        sa.Column("bull_target", sa.Numeric(12, 2)),
        sa.Column("base_case", sa.Text(), nullable=False),
        sa.Column("base_target", sa.Numeric(12, 2)),
        sa.Column("bear_case", sa.Text(), nullable=False),
        sa.Column("bear_target", sa.Numeric(12, 2)),
        # Key analysis
        sa.Column("key_drivers", sa.Text(), nullable=False),
        sa.Column("key_risks", sa.Text(), nullable=False),
        sa.Column("catalysts", sa.Text(), nullable=False),
        # Integrity
        sa.Column("thesis_integrity_score", sa.Numeric(4, 1)),
        sa.Column("integrity_rationale", sa.Text()),
        # Drift
        sa.Column("prior_version_id", UUID(as_uuid=True), sa.ForeignKey("thesis_versions.id", ondelete="RESTRICT")),
        sa.Column("drift_summary", sa.Text()),
        sa.Column("conviction_direction", sa.String(20)),
        sa.Column("llm_model_used", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_thesis_company_version", "thesis_versions", ["company_id", "version"], unique=True)

    # Quarterly Updates
    op.create_table(
        "quarterly_updates",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("company_id", UUID(as_uuid=True), sa.ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("snapshot_id", UUID(as_uuid=True), sa.ForeignKey("financial_snapshots.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("thesis_version_id", UUID(as_uuid=True), sa.ForeignKey("thesis_versions.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("fiscal_year", sa.Integer(), nullable=False),
        sa.Column("fiscal_quarter", sa.Integer(), nullable=False),
        sa.Column("filing_type", sa.String(20), nullable=False),
        sa.Column("executive_summary", sa.Text(), nullable=False),
        sa.Column("key_changes", sa.Text(), nullable=False),
        sa.Column("guidance_update", sa.Text()),
        sa.Column("management_commentary", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_quarterly_company_period", "quarterly_updates", ["company_id", "fiscal_year", "fiscal_quarter"], unique=True)

    # Documents
    op.create_table(
        "documents",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("company_id", UUID(as_uuid=True), sa.ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("doc_type", sa.String(20), nullable=False),
        sa.Column("source", sa.String(20), nullable=False),
        sa.Column("source_url", sa.String(500), nullable=False),
        sa.Column("s3_key", sa.String(500)),
        sa.Column("file_size_bytes", sa.BigInteger()),
        sa.Column("filing_date", sa.String(10)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_documents_company_type", "documents", ["company_id", "doc_type"])


def downgrade() -> None:
    op.drop_table("documents")
    op.drop_table("quarterly_updates")
    op.drop_table("thesis_versions")
    op.drop_table("business_profiles")
    op.drop_table("segments")
    op.drop_table("financial_snapshots")
    op.drop_table("companies")
