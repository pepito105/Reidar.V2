import uuid

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func

from app.core.database import Base


# ---------------------------------------------------------------------------
# Layer 3 — Event Infrastructure (The Agentic Layer)
# events is append-only. Only processed_at, processing_attempts, and
# last_error may be updated after insert. Records are never deleted.
# ---------------------------------------------------------------------------


class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Classification
    event_type = Column(Text, nullable=False)
    # System: company_sourced / company_enriched / signal_detected /
    #   memo_generated / embedding_created / scrape_completed /
    #   yc_batch_published / hn_launch_detected / ph_launch_detected
    # User: pipeline_stage_changed / score_overridden / memo_rated /
    #   outreach_sent / note_added / company_added_manually
    # Integration: email_received / email_sent / calendar_event_created /
    #   transcript_uploaded / slack_message_sent / founder_replied
    # Agent: research_agent_started / research_agent_completed /
    #   pre_meeting_brief_generated / signal_agent_completed /
    #   extraction_agent_completed

    # Scope — NULL for system-wide events (company_sourced, yc_batch_published)
    firm_id = Column(UUID(as_uuid=True), ForeignKey("firms.id"), nullable=True)
    member_id = Column(UUID(as_uuid=True), ForeignKey("firm_members.id"), nullable=True)

    # Entity reference
    entity_type = Column(Text)
    # Values: company / firm / firm_company / interaction / memo /
    #         founder / signal / scrape_job / agent_run
    entity_id = Column(UUID(as_uuid=True))

    # Event data — schema varies by event_type
    payload = Column(JSONB, nullable=False, server_default=text("'{}'"))

    # Webhook deduplication — set for integration events only.
    # INSERT with ON CONFLICT DO NOTHING to handle duplicate deliveries.
    webhook_id = Column(Text, unique=True, nullable=True)

    # Processing state — the only mutable fields after insert
    processed_at = Column(DateTime(timezone=True), nullable=True)
    processing_attempts = Column(Integer, server_default=text("0"))
    last_error = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        Index("idx_events_type", "event_type"),
        # Partial: only index rows where firm_id is set
        Index(
            "idx_events_firm",
            "firm_id",
            postgresql_where=text("firm_id IS NOT NULL"),
        ),
        # Critical: agents poll this index for unprocessed events
        Index(
            "idx_events_unprocessed",
            "created_at",
            postgresql_where=text("processed_at IS NULL"),
        ),
        Index("idx_events_entity", "entity_type", "entity_id"),
        # Partial unique index: dedup enforcement only when webhook_id is set
        Index(
            "idx_events_webhook_id",
            "webhook_id",
            unique=True,
            postgresql_where=text("webhook_id IS NOT NULL"),
        ),
    )


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    agent_type = Column(Text, nullable=False)
    # Values: research_agent / pre_meeting_agent / signal_agent /
    #   extraction_agent / embedding_agent / sourcing_agent /
    #   yc_batch_agent / notification_agent / outreach_agent /
    #   second_encounter_agent

    # Trigger — NULL if manually triggered
    trigger_event_id = Column(
        UUID(as_uuid=True), ForeignKey("events.id"), nullable=True
    )

    # Scope — NULL for global agents (sourcing, yc_batch)
    firm_id = Column(UUID(as_uuid=True), ForeignKey("firms.id"), nullable=True)

    entity_type = Column(Text)
    entity_id = Column(UUID(as_uuid=True))

    # Execution
    status = Column(Text, nullable=False, server_default=text("'running'"))
    # Values: running / completed / failed / timed_out

    started_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_ms = Column(Integer, nullable=True)

    # What the agent did
    actions_taken = Column(JSONB, nullable=False, server_default=text("'[]'"))
    # Array of action records:
    # [{ "action": "fetched_company_data", "source": "harmonic",
    #    "company_id": "...", "success": true },
    #  { "action": "generated_memo", "model": "claude-sonnet-4-5",
    #    "tokens_used": 4821, "success": true }]

    # Output
    output_summary = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, server_default=text("0"))

    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        Index("idx_agent_runs_type", "agent_type"),
        Index(
            "idx_agent_runs_firm",
            "firm_id",
            postgresql_where=text("firm_id IS NOT NULL"),
        ),
        Index("idx_agent_runs_status", "status", "started_at"),
        Index("idx_agent_runs_trigger", "trigger_event_id"),
    )


class ScrapeJob(Base):
    __tablename__ = "scrape_jobs"

    # No firm_id — global Layer 3 infrastructure table

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    source = Column(Text, nullable=False)
    # Values: yc_api / hn_algolia / producthunt / rss_techcrunch /
    #   rss_venturebeat / rss_strictlyvc / brave_search / harmonic

    status = Column(Text, nullable=False, server_default=text("'running'"))
    # Values: running / completed / failed

    # Counts
    companies_found = Column(Integer, server_default=text("0"))
    companies_new = Column(Integer, server_default=text("0"))
    companies_updated = Column(Integer, server_default=text("0"))
    companies_duplicate = Column(Integer, server_default=text("0"))

    # Context
    query = Column(Text, nullable=True)   # search query used (Brave, HN Algolia)
    batch = Column(Text, nullable=True)   # YC batch if applicable (e.g. "S26")

    started_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        Index("idx_scrape_jobs_source", "source", "started_at"),
        Index("idx_scrape_jobs_status", "status"),
    )
