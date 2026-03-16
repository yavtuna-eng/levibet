from sqlalchemy import Column, BigInteger, String, DateTime, Float, JSON
from sqlalchemy.sql import func
from app.db.session import Base


class Match(Base):
    __tablename__ = "matches"

    id = Column(BigInteger, primary_key=True, index=True)
    external_match_id = Column(String, unique=True, nullable=False)
    sport = Column(String, nullable=False)
    league = Column(String, nullable=False)
    season = Column(String)
    home_team = Column(String, nullable=False)
    away_team = Column(String, nullable=False)
    kickoff_at = Column(DateTime(timezone=True), nullable=False, index=True)
    status = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class BayesianTeamStrength(Base):
    __tablename__ = "bayesian_team_strength"

    id = Column(BigInteger, primary_key=True, index=True)
    team_name = Column(String, nullable=False, index=True)
    league = Column(String, nullable=False)
    as_of = Column(DateTime(timezone=True), nullable=False, index=True)
    model_version = Column(String, nullable=False)
    attack_mean = Column(Float, nullable=False)
    attack_std = Column(Float, nullable=False)
    defense_mean = Column(Float, nullable=False)
    defense_std = Column(Float, nullable=False)
    home_adv_mean = Column(Float)
    sample_size = Column(BigInteger)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class FeatureSnapshot(Base):
    __tablename__ = "feature_snapshots"

    id = Column(BigInteger, primary_key=True, index=True)
    match_id = Column(BigInteger, nullable=False, index=True)
    feature_set_version = Column(String, nullable=False)
    as_of = Column(DateTime(timezone=True), nullable=False, index=True)
    features = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(BigInteger, primary_key=True, index=True)
    match_id = Column(BigInteger, nullable=False, index=True)
    model_version = Column(String, nullable=False)
    as_of = Column(DateTime(timezone=True), nullable=False, index=True)
    home_win_prob = Column(Float, nullable=False)
    draw_prob = Column(Float, nullable=True)
    away_win_prob = Column(Float, nullable=False)
    confidence_score = Column(Float)
    edge_score = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Signal(Base):
    __tablename__ = "signals"

    id = Column(BigInteger, primary_key=True, index=True)
    prediction_id = Column(BigInteger, nullable=False)
    channel_name = Column(String, nullable=False)
    telegram_message_id = Column(String)
    dispatched_at = Column(DateTime(timezone=True))
    status = Column(String, nullable=False, default="pending")
