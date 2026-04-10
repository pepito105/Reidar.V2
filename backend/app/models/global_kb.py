import uuid

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from app.core.database import Base


# ---------------------------------------------------------------------------
# Layer 1 — Global Knowledge Base
# No firm_id on any table in this layer. Schema Rule #1.
# ---------------------------------------------------------------------------


class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identity
    name = Column(Text, nullable=False)
    slug = Column(Text, unique=True, nullable=False)
    website = Column(Text)
    domain = Column(Text)

    # Description
    one_liner = Column(Text)
    description = Column(Text)
    business_model = Column(Text)
    target_customer = Column(Text)

    # Classification
    sector = Column(Text)
    subsector = Column(Text)
    tags = Column(ARRAY(Text))
    ai_nativeness = Column(SmallInteger)

    # Stage & Funding
    stage = Column(Text)
    total_raised_usd = Column(BigInteger)
    last_round_type = Column(Text)
    last_round_usd = Column(BigInteger)
    last_round_date = Column(Date)
    valuation_usd = Column(BigInteger)

    # Team
    employee_count = Column(Integer)
    founding_year = Column(Integer)
    headquarters = Column(Text)

    # Source tracking
    source = Column(Text, nullable=False)
    source_url = Column(Text)
    source_batch = Column(Text)
    harmonic_id = Column(Text)
    yc_id = Column(Text)

    # Quality
    enrichment_status = Column(Text, default="raw")
    last_enriched_at = Column(DateTime(timezone=True))

    # Timestamps
    founded_at = Column(Date)
    scraped_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        Index("idx_companies_domain", "domain"),
        Index("idx_companies_sector", "sector"),
        Index("idx_companies_stage", "stage"),
        Index("idx_companies_source", "source"),
        Index("idx_companies_created_at", "created_at"),
    )


class Founder(Base):
    __tablename__ = "founders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identity
    name = Column(Text, nullable=False)
    email = Column(Text)
    linkedin_url = Column(Text)
    twitter_url = Column(Text)

    # Background
    prior_companies = Column(ARRAY(Text))
    prior_roles = Column(ARRAY(Text))
    education = Column(ARRAY(Text))
    domain_years = Column(Integer)

    # Founder signals
    prior_exits = Column(Boolean, default=False)
    repeat_founder = Column(Boolean, default=False)
    technical = Column(Boolean)
    domain_expert = Column(Boolean)

    # Source
    source = Column(Text)
    source_url = Column(Text)

    # Timestamps
    scraped_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class CompanyFounder(Base):
    __tablename__ = "company_founders"

    company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    founder_id = Column(
        UUID(as_uuid=True),
        ForeignKey("founders.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    role = Column(Text)
    is_primary = Column(Boolean, default=False)


class Investor(Base):
    __tablename__ = "investors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    type = Column(Text)
    tier = Column(SmallInteger)
    focus_stages = Column(ARRAY(Text))
    focus_sectors = Column(ARRAY(Text))
    website = Column(Text)
    crunchbase_url = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class FundingRound(Base):
    __tablename__ = "funding_rounds"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    round_type = Column(Text, nullable=False)
    amount_usd = Column(BigInteger)
    valuation_usd = Column(BigInteger)
    announced_date = Column(Date)
    closed_date = Column(Date)
    lead_investor = Column(Text)
    notable_investors = Column(ARRAY(Text))
    source_url = Column(Text)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        Index("idx_funding_rounds_company", "company_id"),
        Index("idx_funding_rounds_date", "announced_date"),
    )


class RoundInvestor(Base):
    __tablename__ = "round_investors"

    round_id = Column(
        UUID(as_uuid=True),
        ForeignKey("funding_rounds.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    investor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("investors.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    is_lead = Column(Boolean, default=False)


class GlobalSignal(Base):
    __tablename__ = "global_signals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    signal_type = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    summary = Column(Text)
    source_url = Column(Text, nullable=False)
    source_name = Column(Text)
    signal_strength = Column(SmallInteger)
    sentiment = Column(Text)
    published_at = Column(DateTime(timezone=True))
    detected_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    __table_args__ = (
        Index("idx_global_signals_company", "company_id"),
        Index("idx_global_signals_type", "signal_type"),
        Index("idx_global_signals_detected", "detected_at"),
    )


class CompanyEmbedding(Base):
    """Pool 1 embeddings. firm_id is ALWAYS NULL. Enforced by CHECK constraint."""

    __tablename__ = "company_embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    firm_id = Column(UUID(as_uuid=True), nullable=True, default=None)
    embedding_type = Column(Text, nullable=False)
    content_hash = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=False)
    model_version = Column(Text, nullable=False, default="text-embedding-3-small")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("firm_id IS NULL", name="pool1_no_firm_id"),
        Index("idx_company_embeddings_company", "company_id"),
        Index("idx_company_embeddings_type", "embedding_type"),
    )
