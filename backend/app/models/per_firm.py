import uuid

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from app.core.database import Base


# ---------------------------------------------------------------------------
# Layer 2 — Per-Firm Intelligence
# Every table in this layer has firm_id. Every query must be scoped by
# firm_id. Schema Rule #2. No exceptions.
# ---------------------------------------------------------------------------


class Firm(Base):
    __tablename__ = "firms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identity
    name = Column(Text, nullable=False)
    slug = Column(Text, nullable=False, unique=True)
    website = Column(Text, nullable=True)

    # Auth mapping
    clerk_org_id = Column(Text, nullable=True, unique=True)
    owner_user_id = Column(Text, nullable=False)

    # Investment Mandate — structured fields
    thesis_text = Column(Text, nullable=True)
    focus_stages = Column(ARRAY(Text), nullable=False, server_default="{}")
    focus_sectors = Column(ARRAY(Text), nullable=False, server_default="{}")
    focus_geographies = Column(ARRAY(Text), nullable=False, server_default="{}")
    check_size_min_usd = Column(BigInteger, nullable=True)
    check_size_max_usd = Column(BigInteger, nullable=True)
    excluded_sectors = Column(ARRAY(Text), nullable=False, server_default="{}")
    excluded_business_models = Column(ARRAY(Text), nullable=False, server_default="{}")
    ai_nativeness_min = Column(SmallInteger, nullable=True, server_default="1")
    coverage_threshold = Column(SmallInteger, nullable=True, server_default="3")

    # Firm context for reasoning
    portfolio_companies = Column(ARRAY(Text), nullable=True)
    notable_investments = Column(ARRAY(Text), nullable=True)
    typical_pass_reasons = Column(ARRAY(Text), nullable=True)

    # Notification preferences
    notification_emails = Column(ARRAY(Text), nullable=False, server_default="{}")
    weekly_digest_enabled = Column(Boolean, nullable=True, server_default="true")
    top_match_alerts_enabled = Column(Boolean, nullable=True, server_default="true")
    signal_alerts_enabled = Column(Boolean, nullable=True, server_default="true")

    # Slack integration
    slack_workspace_id = Column(Text, nullable=True)
    slack_bot_token = Column(Text, nullable=True)
    slack_channel_id = Column(Text, nullable=True)

    # Status
    is_active = Column(Boolean, nullable=True, server_default="true")
    onboarded_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        Index("idx_firms_clerk_org", "clerk_org_id"),
        Index("idx_firms_owner", "owner_user_id"),
    )


class FirmMember(Base):
    __tablename__ = "firm_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firm_id = Column(
        UUID(as_uuid=True),
        ForeignKey("firms.id", ondelete="CASCADE"),
        nullable=False,
    )

    clerk_user_id = Column(Text, nullable=False, unique=True)
    name = Column(Text, nullable=False)
    email = Column(Text, nullable=False)
    role = Column(Text, nullable=False)  # gp / partner / principal / associate / analyst

    # Gmail integration (per-member, not per-firm)
    gmail_connected = Column(Boolean, nullable=True, server_default="false")
    gmail_access_token = Column(Text, nullable=True)    # encrypted
    gmail_refresh_token = Column(Text, nullable=True)   # encrypted
    gmail_token_expiry = Column(DateTime(timezone=True), nullable=True)
    gmail_last_synced = Column(DateTime(timezone=True), nullable=True)
    gmail_email = Column(Text, nullable=True)

    # Calendar integration
    calendar_connected = Column(Boolean, nullable=True, server_default="false")
    calendar_access_token = Column(Text, nullable=True)   # encrypted
    calendar_refresh_token = Column(Text, nullable=True)  # encrypted

    is_active = Column(Boolean, nullable=True, server_default="true")
    joined_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        Index("idx_firm_members_firm", "firm_id"),
        Index("idx_firm_members_clerk", "clerk_user_id"),
    )


class FirmCompany(Base):
    __tablename__ = "firm_companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firm_id = Column(
        UUID(as_uuid=True),
        ForeignKey("firms.id", ondelete="CASCADE"),
        nullable=False,
    )
    company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Pipeline state
    pipeline_stage = Column(
        Text, nullable=False, server_default="watching"
    )
    # watching / outreach / first_call / diligence / ic_review /
    # term_sheet / closed / passed / invested / portfolio
    pipeline_entered_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Mandate scoring
    fit_score = Column(SmallInteger, nullable=True)
    fit_score_rationale = Column(Text, nullable=True)
    ai_nativeness_score = Column(SmallInteger, nullable=True)

    # Analyst override
    analyst_fit_score = Column(SmallInteger, nullable=True)
    analyst_override_reason = Column(Text, nullable=True)
    overridden_by = Column(
        UUID(as_uuid=True),
        ForeignKey("firm_members.id"),
        nullable=True,
    )
    overridden_at = Column(DateTime(timezone=True), nullable=True)

    # Pass tracking
    passed_at = Column(DateTime(timezone=True), nullable=True)
    pass_category = Column(Text, nullable=True)
    pass_reason_official = Column(Text, nullable=True)
    pass_reason_internal = Column(Text, nullable=True)
    pass_what_would_change = Column(Text, nullable=True)

    # Conviction tracking
    conviction_level = Column(Text, nullable=True)
    # exploring / interested / excited / high_conviction / champion
    champion_member_id = Column(
        UUID(as_uuid=True),
        ForeignKey("firm_members.id"),
        nullable=True,
    )

    # Notes
    notes = Column(Text, nullable=True)
    internal_memo = Column(Text, nullable=True)

    # Outreach tracking
    first_outreach_at = Column(DateTime(timezone=True), nullable=True)
    last_outreach_at = Column(DateTime(timezone=True), nullable=True)
    outreach_method = Column(Text, nullable=True)
    intro_path = Column(Text, nullable=True)

    # Second encounter support
    previously_seen = Column(Boolean, nullable=True, server_default="false")
    previous_pass_id = Column(
        UUID(as_uuid=True),
        ForeignKey("firm_companies.id"),
        nullable=True,
    )

    # Research state
    last_researched_at = Column(DateTime(timezone=True), nullable=True)
    research_status = Column(Text, nullable=True, server_default="pending")
    # pending / in_progress / complete / stale

    # Metadata
    added_by = Column(
        UUID(as_uuid=True),
        ForeignKey("firm_members.id"),
        nullable=True,
    )
    added_source = Column(Text, nullable=True)
    # coverage / manual / email_inbound / import / research_agent

    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("firm_id", "company_id"),
        Index("idx_firm_companies_firm", "firm_id"),
        Index("idx_firm_companies_company", "company_id"),
        Index("idx_firm_companies_stage", "firm_id", "pipeline_stage"),
        Index("idx_firm_companies_fit", "firm_id", "fit_score"),
    )


class PipelineStageTransition(Base):
    __tablename__ = "pipeline_stage_transitions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firm_id = Column(
        UUID(as_uuid=True),
        ForeignKey("firms.id", ondelete="CASCADE"),
        nullable=False,
    )
    firm_company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("firm_companies.id", ondelete="CASCADE"),
        nullable=False,
    )

    from_stage = Column(Text, nullable=True)   # NULL if this is the first stage entry
    to_stage = Column(Text, nullable=False)

    transitioned_by = Column(
        UUID(as_uuid=True),
        ForeignKey("firm_members.id"),
        nullable=True,
    )
    transition_type = Column(Text, nullable=False)
    # manual / agent_triggered / email_reply / calendar_event /
    # signal_triggered / timeout

    reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # Timing signal: how many days in from_stage before this transition?
    days_in_prior_stage = Column(Integer, nullable=True)

    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        Index("idx_transitions_firm", "firm_id"),
        Index("idx_transitions_firm_company", "firm_company_id"),
        Index("idx_transitions_created", "created_at"),
    )


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firm_id = Column(
        UUID(as_uuid=True),
        ForeignKey("firms.id", ondelete="CASCADE"),
        nullable=False,
    )
    firm_company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("firm_companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    member_id = Column(
        UUID(as_uuid=True),
        ForeignKey("firm_members.id"),
        nullable=True,
    )

    interaction_type = Column(Text, nullable=False)
    # email_inbound / email_outbound / call / meeting / demo /
    # reference_check / conference_meeting / lp_intro /
    # document_received / transcript_ingested / note_added /
    # co_investor_call / technical_review / customer_call

    # Raw artifact
    raw_content = Column(Text, nullable=True)
    subject = Column(Text, nullable=True)
    participants = Column(JSONB, nullable=True)
    # Structured participant objects — NOT TEXT[].
    # [{ "name": "...", "email": "...", "role": "...",
    #    "affiliation": "...", "type": "investor|founder|other" }]
    direction = Column(Text, nullable=True)   # inbound / outbound / internal

    # Parsed metadata
    occurred_at = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, nullable=True)

    # Source tracking
    source = Column(Text, nullable=False)
    # gmail_sync / calendar_sync / manual / transcript_upload /
    # granola / otter / fathom / fireflies
    gmail_message_id = Column(Text, nullable=True)
    calendar_event_id = Column(Text, nullable=True)
    transcript_url = Column(Text, nullable=True)

    # Extraction state
    extraction_status = Column(Text, nullable=True, server_default="pending")
    # pending / processing / complete / failed
    extracted_at = Column(DateTime(timezone=True), nullable=True)

    # Sentiment (extracted by Claude Haiku)
    overall_sentiment = Column(Text, nullable=True)   # positive / neutral / negative / mixed
    conviction_delta = Column(Text, nullable=True)    # increased / decreased / unchanged / unclear

    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        Index("idx_interactions_firm", "firm_id"),
        Index("idx_interactions_firm_company", "firm_company_id"),
        Index("idx_interactions_type", "firm_id", "interaction_type"),
        Index("idx_interactions_occurred", "occurred_at"),
        Index(
            "idx_interactions_extraction",
            "extraction_status",
            postgresql_where=text("extraction_status = 'pending'"),
        ),
    )


class FirmReasoningSignal(Base):
    __tablename__ = "firm_reasoning_signals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firm_id = Column(
        UUID(as_uuid=True),
        ForeignKey("firms.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Source linkage
    interaction_id = Column(
        UUID(as_uuid=True),
        ForeignKey("interactions.id", ondelete="SET NULL"),
        nullable=True,
    )
    firm_company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("firm_companies.id", ondelete="CASCADE"),
        nullable=True,
    )

    # Signal classification
    signal_type = Column(Text, nullable=False)
    # partner_objection / conviction_trigger / pass_reasoning /
    # threshold_signal / founder_signal / market_signal / open_question /
    # thesis_refinement / comparable_reference / champion_signal /
    # red_flag / behavioral_signal / second_encounter / intro_path /
    # calendar_pattern / network_signal / velocity_signal

    # Entity scope
    entity_type = Column(Text, nullable=True)
    # company / founder / sector / stage / fund_thesis / partner
    entity_id = Column(UUID(as_uuid=True), nullable=True)
    # UUID of related entity — no FK (polymorphic reference)

    # Signal content (structured, extracted by Claude Haiku)
    structured_data = Column(JSONB, nullable=False, server_default="{}")
    signal_text = Column(Text, nullable=False)
    # Human-readable summary written by Claude Haiku. This is what gets embedded.

    # Quality
    confidence = Column(Text, nullable=True, server_default="medium")
    # high / medium / low
    extraction_model = Column(
        Text, nullable=True, server_default="claude-haiku-4-5-20251001"
    )

    # Temporal context
    signal_date = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        Index("idx_reasoning_signals_firm", "firm_id"),
        Index("idx_reasoning_signals_type", "firm_id", "signal_type"),
        Index("idx_reasoning_signals_entity", "entity_id"),
        Index("idx_reasoning_signals_company", "firm_company_id"),
    )


class ScoreDelta(Base):
    __tablename__ = "score_deltas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firm_id = Column(
        UUID(as_uuid=True),
        ForeignKey("firms.id", ondelete="CASCADE"),
        nullable=False,
    )
    firm_company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("firm_companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    member_id = Column(
        UUID(as_uuid=True),
        ForeignKey("firm_members.id"),
        nullable=True,
    )

    delta_type = Column(Text, nullable=False)
    # fit_score / ai_nativeness / pipeline_stage / next_step_recommendation /
    # memo_team_section / memo_market_section / memo_competitive_section /
    # memo_conclusion / memo_bull_case / memo_risks

    reidar_value = Column(Text, nullable=False)
    human_value = Column(Text, nullable=False)

    delta_direction = Column(Text, nullable=True)   # higher / lower / different
    reason = Column(Text, nullable=True)
    context_at_time = Column(JSONB, nullable=True)

    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        Index("idx_score_deltas_firm", "firm_id"),
        Index("idx_score_deltas_type", "firm_id", "delta_type"),
    )


class OutreachEvent(Base):
    __tablename__ = "outreach_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firm_id = Column(
        UUID(as_uuid=True),
        ForeignKey("firms.id", ondelete="CASCADE"),
        nullable=False,
    )
    firm_company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("firm_companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    member_id = Column(
        UUID(as_uuid=True),
        ForeignKey("firm_members.id"),
        nullable=True,
    )

    outreach_type = Column(Text, nullable=False)
    # cold_email / warm_intro_request / warm_intro_sent /
    # linkedin_dm / conference_followup / inbound_response / re_engagement

    # Intro path (if warm)
    intro_via = Column(Text, nullable=True)
    intro_relationship = Column(Text, nullable=True)
    # portfolio_founder / lp / co_investor / advisor / personal / conference

    # Message analysis (extracted by Claude Haiku)
    thesis_framing = Column(Text, nullable=True)
    first_question = Column(Text, nullable=True)

    # Response tracking
    founder_responded = Column(Boolean, nullable=True, server_default="false")
    response_hours = Column(Integer, nullable=True)
    founder_response_tone = Column(Text, nullable=True)
    # eager / professional / lukewarm / no_response

    # Outcome
    resulted_in_call = Column(Boolean, nullable=True, server_default="false")

    sent_at = Column(DateTime(timezone=True), nullable=False)
    responded_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        Index("idx_outreach_firm", "firm_id"),
        Index("idx_outreach_firm_company", "firm_company_id"),
    )


class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firm_id = Column(
        UUID(as_uuid=True),
        ForeignKey("firms.id", ondelete="CASCADE"),
        nullable=False,
    )
    member_id = Column(
        UUID(as_uuid=True),
        ForeignKey("firm_members.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Raw calendar data
    calendar_event_id = Column(Text, nullable=False)   # external calendar provider ID
    title = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    location = Column(Text, nullable=True)

    # Timing
    started_at = Column(DateTime(timezone=True), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, nullable=True)

    # Attendees (structured — same JSONB pattern as interactions.participants)
    attendees = Column(JSONB, nullable=True)
    # [{ "name": "...", "email": "...", "role": "...", "affiliation": "..." }]

    # Recurrence
    is_recurring = Column(Boolean, nullable=True, server_default="false")
    recurrence_rule = Column(Text, nullable=True)   # RRULE string
    recurrence_parent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("calendar_events.id"),
        nullable=True,
    )

    # Company matching state
    matching_status = Column(Text, nullable=True, server_default="pending")
    # pending / matched / no_match / ambiguous
    matched_company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.id"),
        nullable=True,
    )
    matched_firm_company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("firm_companies.id"),
        nullable=True,
    )
    match_confidence = Column(Text, nullable=True)   # high / medium / low

    # Downstream linkage — set after matched event creates an interactions record
    interaction_id = Column(
        UUID(as_uuid=True),
        ForeignKey("interactions.id"),
        nullable=True,
    )

    # Source
    source = Column(Text, nullable=False, server_default="google_calendar")
    raw_payload = Column(JSONB, nullable=True)

    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        Index("idx_calendar_events_firm", "firm_id"),
        Index("idx_calendar_events_member", "member_id"),
        Index("idx_calendar_events_started", "started_at"),
        Index(
            "idx_calendar_events_matching",
            "matching_status",
            postgresql_where=text(
                "matching_status = 'pending'"
            ),
        ),
        Index(
            "idx_calendar_events_company",
            "matched_company_id",
            postgresql_where=text(
                "matched_company_id IS NOT NULL"
            ),
        ),
    )


class SlackMessage(Base):
    __tablename__ = "slack_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firm_id = Column(
        UUID(as_uuid=True),
        ForeignKey("firms.id", ondelete="CASCADE"),
        nullable=False,
    )
    member_id = Column(
        UUID(as_uuid=True),
        ForeignKey("firm_members.id"),
        nullable=True,
    )

    # Slack metadata
    slack_message_id = Column(Text, nullable=False, unique=True)   # Slack ts identifier
    slack_channel_id = Column(Text, nullable=False)
    slack_channel_name = Column(Text, nullable=True)
    slack_thread_ts = Column(Text, nullable=True)   # NULL if not a thread reply
    slack_user_id = Column(Text, nullable=True)

    # Content
    raw_content = Column(Text, nullable=False)
    message_type = Column(Text, nullable=False)
    # post_call_reaction / deal_commentary / partner_discussion /
    # intro_request / signal_share / pass_discussion /
    # conviction_signal / question / general

    # Company linkage (may be NULL if not yet matched)
    firm_company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("firm_companies.id"),
        nullable=True,
    )
    company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.id"),
        nullable=True,
    )

    # Timing
    sent_at = Column(DateTime(timezone=True), nullable=False)

    # Extraction state
    extraction_status = Column(Text, nullable=True, server_default="pending")
    # pending / processing / complete / failed
    extracted_at = Column(DateTime(timezone=True), nullable=True)

    # Extracted signals (high-level, before full extraction pipeline)
    detected_sentiment = Column(Text, nullable=True)    # positive / negative / neutral / mixed
    detected_conviction = Column(Text, nullable=True)   # increasing / decreasing / unchanged
    mentions_company = Column(Boolean, nullable=True, server_default="false")
    mentions_founder = Column(Boolean, nullable=True, server_default="false")

    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        Index("idx_slack_messages_firm", "firm_id"),
        Index(
            "idx_slack_messages_company",
            "firm_company_id",
            postgresql_where=text(
                "firm_company_id IS NOT NULL"
            ),
        ),
        Index("idx_slack_messages_sent", "sent_at"),
        Index(
            "idx_slack_messages_extraction",
            "extraction_status",
            postgresql_where=text(
                "extraction_status = 'pending'"
            ),
        ),
        Index("idx_slack_messages_type", "firm_id", "message_type"),
    )


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firm_id = Column(
        UUID(as_uuid=True),
        ForeignKey("firms.id", ondelete="CASCADE"),
        nullable=False,
    )
    firm_company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("firm_companies.id"),
        nullable=True,
    )
    # NULL if document arrived before company was matched

    # Document identity
    document_type = Column(Text, nullable=False)
    # pitch_deck / one_pager / financial_model / cap_table /
    # technical_dd / reference_doc / term_sheet / loi /
    # portfolio_update / market_map / other

    title = Column(Text, nullable=True)
    file_name = Column(Text, nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    mime_type = Column(Text, nullable=True)

    # Source
    source = Column(Text, nullable=False)
    # email_attachment / shared_link / uploaded / slack_share

    source_interaction_id = Column(
        UUID(as_uuid=True),
        ForeignKey("interactions.id"),
        nullable=True,
    )
    # The interaction record that delivered this document (email case).

    source_slack_message_id = Column(
        UUID(as_uuid=True),
        ForeignKey("slack_messages.id"),
        nullable=True,
    )
    # The slack_messages record that delivered this document (slack_share case).
    # Exactly one of source_interaction_id or source_slack_message_id should be
    # set depending on source. Both may be NULL for manually uploaded documents.

    # Storage
    storage_url = Column(Text, nullable=True)
    content_hash = Column(Text, nullable=True)   # for deduplication across re-sends

    # Engagement tracking
    first_opened_at = Column(DateTime(timezone=True), nullable=True)
    last_opened_at = Column(DateTime(timezone=True), nullable=True)
    open_count = Column(Integer, nullable=True, server_default="0")
    forwarded_to = Column(JSONB, nullable=True)
    # [{ "name": "...", "email": "...", "forwarded_at": "..." }]
    # Forwarding behavior is a conviction and network signal.

    re_requested = Column(Boolean, nullable=True, server_default="false")
    # Did the firm ask the founder to resend or update this document?

    # Extraction state
    extraction_status = Column(Text, nullable=True, server_default="pending")
    # pending / processing / complete / failed / skipped
    extracted_at = Column(DateTime(timezone=True), nullable=True)
    extracted_data = Column(JSONB, nullable=True)
    # For pitch_deck: { "problem": "...", "solution": "...",
    # "market_size": "...", "traction": "...", "ask": "..." }

    received_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        Index("idx_documents_firm", "firm_id"),
        Index(
            "idx_documents_firm_company",
            "firm_company_id",
            postgresql_where=text(
                "firm_company_id IS NOT NULL"
            ),
        ),
        Index("idx_documents_type", "firm_id", "document_type"),
        Index(
            "idx_documents_extraction",
            "extraction_status",
            postgresql_where=text(
                "extraction_status = 'pending'"
            ),
        ),
        Index("idx_documents_received", "received_at"),
    )


class FirmEmbedding(Base):
    __tablename__ = "firm_embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firm_id = Column(
        UUID(as_uuid=True),
        ForeignKey("firms.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Source linkage
    source_type = Column(Text, nullable=False)
    # reasoning_signal / interaction_summary / thesis_statement /
    # pass_pattern / conviction_pattern / memo_section

    source_id = Column(UUID(as_uuid=True), nullable=False)
    # UUID of the source record — no FK (polymorphic reference across tables)

    # Scope for retrieval filtering
    related_company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.id"),
        nullable=True,
    )
    related_sector = Column(Text, nullable=True)
    related_stage = Column(Text, nullable=True)
    signal_type = Column(Text, nullable=True)   # mirrors firm_reasoning_signals.signal_type

    # The embedded content
    content_text = Column(Text, nullable=False)
    content_hash = Column(Text, nullable=False)

    embedding = Column(Vector(1536), nullable=False)
    model_version = Column(
        Text, nullable=False, server_default="text-embedding-3-small"
    )

    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Pool 2: firm_id MUST be set. Enforced at DB level. Schema Rule #3.
    __table_args__ = (
        CheckConstraint("firm_id IS NOT NULL", name="pool2_requires_firm_id"),
        Index("idx_firm_embeddings_firm", "firm_id"),
        Index("idx_firm_embeddings_source", "firm_id", "source_type"),
        Index("idx_firm_embeddings_company", "related_company_id"),
        Index("idx_firm_embeddings_sector", "firm_id", "related_sector"),
        # ivfflat vector index added manually in migration via op.execute().
        # Autogenerate does not produce pgvector custom index types.
    )


class InvestmentMemo(Base):
    __tablename__ = "investment_memos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firm_id = Column(
        UUID(as_uuid=True),
        ForeignKey("firms.id", ondelete="CASCADE"),
        nullable=False,
    )
    firm_company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("firm_companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    version = Column(Integer, nullable=False, server_default="1")

    # Generated content (all produced by Claude Sonnet)
    positioning = Column(Text, nullable=True)
    what_they_do = Column(Text, nullable=True)
    market_timing = Column(Text, nullable=True)

    fit_score = Column(SmallInteger, nullable=True)
    fit_rationale = Column(Text, nullable=True)
    thesis_alignment = Column(Text, nullable=True)
    thesis_gaps = Column(Text, nullable=True)

    traction_signals = Column(Text, nullable=True)
    team_assessment = Column(Text, nullable=True)
    competitive_landscape = Column(Text, nullable=True)

    risks = Column(JSONB, nullable=True)
    # [{ "risk": "...", "likelihood": "high/medium/low",
    #    "impact": "critical/major/moderate/minor", "mitigation": "..." }]

    comparables = Column(JSONB, nullable=True)
    # [{ "company": "...", "differentiation": "...",
    #    "from_portfolio": true/false, "outcome": "..." }]

    bull_case = Column(Text, nullable=True)
    recommended_next_step = Column(Text, nullable=True)
    # pass / monitor / request_intro / diligence
    conviction_level = Column(Text, nullable=True)
    # pass / watch / interested / excited / high_conviction

    # RAG context used (for auditability)
    pool1_records_used = Column(Integer, nullable=True)
    pool2_records_used = Column(Integer, nullable=True)
    pool2_signals_used = Column(JSONB, nullable=True)

    # Generation metadata
    model_used = Column(Text, nullable=False, server_default="claude-sonnet-4-5")
    generated_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Human feedback
    analyst_rating = Column(SmallInteger, nullable=True)
    analyst_notes = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("firm_company_id", "version"),
        Index("idx_memos_firm", "firm_id"),
        Index("idx_memos_firm_company", "firm_company_id"),
    )


class FirmNotification(Base):
    __tablename__ = "firm_notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firm_id = Column(
        UUID(as_uuid=True),
        ForeignKey("firms.id", ondelete="CASCADE"),
        nullable=False,
    )
    member_id = Column(
        UUID(as_uuid=True),
        ForeignKey("firm_members.id"),
        nullable=True,
    )
    # NULL = notification for the whole firm. Set = for a specific member.

    notification_type = Column(Text, nullable=False)
    # new_top_match / new_strong_fit / signal_on_pipeline_company /
    # pre_meeting_brief / stale_deal / second_encounter /
    # research_complete / weekly_digest / thesis_pattern_detected /
    # conviction_shift_detected / agent_action_taken

    title = Column(Text, nullable=False)
    body = Column(Text, nullable=True)

    related_company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.id"),
        nullable=True,
    )

    # FK to events.id intentionally omitted here.
    # The events table is created in the Layer 3 migration. Adding the FK
    # constraint now would cause the Layer 2 migration to fail because the
    # events table does not yet exist. The FK will be added via ALTER TABLE
    # in the Layer 3 migration.
    related_event_id = Column(UUID(as_uuid=True), nullable=True)

    # Delivery
    delivered_in_app = Column(Boolean, nullable=True, server_default="false")
    delivered_via_slack = Column(Boolean, nullable=True, server_default="false")
    delivered_via_email = Column(Boolean, nullable=True, server_default="false")

    read_at = Column(DateTime(timezone=True), nullable=True)
    acted_on_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        Index("idx_notifications_firm", "firm_id"),
        Index(
            "idx_notifications_unread",
            "firm_id",
            "read_at",
            postgresql_where=text(
                "read_at IS NULL"
            ),
        ),
    )
