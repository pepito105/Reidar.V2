def test_all_models_have_correct_tablenames():
    from app.models.global_kb import (
        Company, Founder, CompanyFounder,
        Investor, FundingRound, RoundInvestor,
        GlobalSignal, CompanyEmbedding,
    )
    assert Company.__tablename__ == "companies"
    assert Founder.__tablename__ == "founders"
    assert CompanyFounder.__tablename__ == "company_founders"
    assert Investor.__tablename__ == "investors"
    assert FundingRound.__tablename__ == "funding_rounds"
    assert RoundInvestor.__tablename__ == "round_investors"
    assert GlobalSignal.__tablename__ == "global_signals"
    assert CompanyEmbedding.__tablename__ == "company_embeddings"


def test_company_has_required_columns():
    from app.models.global_kb import Company
    col_names = {c.name for c in Company.__table__.columns}
    for col in [
        "id", "name", "slug", "domain", "sector", "stage",
        "source", "scraped_at", "updated_at", "created_at",
        "one_liner", "description", "tags", "ai_nativeness",
        "total_raised_usd", "last_round_type", "founding_year",
        "enrichment_status", "harmonic_id", "yc_id",
    ]:
        assert col in col_names, f"Company missing column: {col}"


def test_no_firm_id_on_layer1_tables():
    """Layer 1 tables must NEVER have a firm_id column. Schema Rule #1."""
    from app.models.global_kb import Company, Founder, Investor, FundingRound, GlobalSignal
    for model in [Company, Founder, Investor, FundingRound, GlobalSignal]:
        col_names = {c.name for c in model.__table__.columns}
        assert "firm_id" not in col_names, (
            f"{model.__name__} must not have firm_id (Layer 1 tables are global)"
        )


def test_company_embedding_pool1_check_constraint():
    """Pool 1 embeddings must enforce firm_id IS NULL at DB level. Schema Rule #3."""
    from app.models.global_kb import CompanyEmbedding
    from sqlalchemy import CheckConstraint
    check_names = {
        c.name for c in CompanyEmbedding.__table__.constraints
        if isinstance(c, CheckConstraint)
    }
    assert "pool1_no_firm_id" in check_names


def test_company_embedding_has_vector_column():
    from app.models.global_kb import CompanyEmbedding
    from pgvector.sqlalchemy import Vector
    col = CompanyEmbedding.__table__.c.embedding
    assert isinstance(col.type, Vector)


def test_funding_round_fk_to_companies():
    from app.models.global_kb import FundingRound
    fk_targets = {
        list(col.foreign_keys)[0].target_fullname
        for col in FundingRound.__table__.columns
        if col.foreign_keys
    }
    assert "companies.id" in fk_targets


def test_global_signal_fk_to_companies():
    from app.models.global_kb import GlobalSignal
    fk_targets = {
        list(col.foreign_keys)[0].target_fullname
        for col in GlobalSignal.__table__.columns
        if col.foreign_keys
    }
    assert "companies.id" in fk_targets


def test_company_founder_composite_pk():
    from app.models.global_kb import CompanyFounder
    pk_cols = {c.name for c in CompanyFounder.__table__.primary_key.columns}
    assert pk_cols == {"company_id", "founder_id"}


def test_round_investor_composite_pk():
    from app.models.global_kb import RoundInvestor
    pk_cols = {c.name for c in RoundInvestor.__table__.primary_key.columns}
    assert pk_cols == {"round_id", "investor_id"}
