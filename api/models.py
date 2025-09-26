"""SQLAlchemy models for existing and new tables"""
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime
from sqlalchemy.sql import func
from .database import Base

# EXISTING TABLES (Read-only)
class CurrentBestLine(Base):
    __tablename__ = "current_best_lines"
    player = Column(String, primary_key=True)
    market = Column(String, primary_key=True)
    book = Column(String, primary_key=True)
    line = Column(Float)
    pos = Column(String)
    over_odds = Column(Integer)
    under_odds = Column(Integer)
    updated_at = Column(String)
    event_id = Column(String)
    commence_time = Column(String)
    home_team = Column(String)
    away_team = Column(String)
    season = Column(Integer)
    week = Column(Integer)
    team_code = Column(String)
    opponent_def_code = Column(String)
    is_stale = Column(Integer)

class Event(Base):
    __tablename__ = "events"
    event_id = Column(String, primary_key=True)
    sport_key = Column(String)
    commence_time = Column(String)
    home_team = Column(String)
    away_team = Column(String)
    season = Column(Integer)
    week = Column(Integer)

# NEW USER TABLES
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    external_id = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

class UserBet(Base):
    __tablename__ = "user_bets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    external_user_id = Column(String(255), nullable=False, index=True)
    game_id = Column(String(255), nullable=False)
    market = Column(String(50), nullable=False)
    selection = Column(String(50), nullable=False)
    stake = Column(Float, nullable=False)
    odds = Column(Float, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    notes = Column(Text, nullable=True)
    clv_cents = Column(Float, nullable=True)
    beat_close = Column(Boolean, nullable=True)
    is_settled = Column(Boolean, default=False, nullable=False)

class DigestSubscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    frequency = Column(String(50), default="weekly", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
