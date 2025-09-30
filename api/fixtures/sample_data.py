"""Sample data fixtures for testing the betting platform"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, cast

from sqlalchemy.orm import Session

from ..crud import bet_crud, edge_crud, transaction_crud, user_crud
from ..models import (
    Bet,
    BetStatus,
    Edge,
    EdgeStatus,
    Event,
    Transaction,
    TransactionStatus,
    TransactionType,
    User,
    UserStatus,
)


def create_sample_users(db: Session) -> List[User]:
    """Create sample users for testing"""
    sample_users = [
        {
            "external_id": "user_001_test",
            "email": "john.doe@example.com",
            "name": "John Doe",
            "first_name": "John",
            "last_name": "Doe",
            "timezone": "America/New_York",
            "phone": "+1-555-0101",
            "status": UserStatus.ACTIVE,
            "is_active": True,
            "is_verified": True,
            "verification_level": "enhanced",
            "max_bet_size": Decimal("2500.00"),
            "daily_bet_limit": Decimal("10000.00"),
            "monthly_bet_limit": Decimal("100000.00"),
            "risk_tolerance": "high",
            "auto_kelly_sizing": True,
            "max_kelly_fraction": 0.20,
            "preferred_sports": '["nfl", "nba"]',
            "notification_preferences": '{"email": true, "push": true, "sms": false}',
            "ui_preferences": '{"theme": "dark", "currency": "USD"}',
        },
        {
            "external_id": "user_002_test",
            "email": "jane.smith@example.com",
            "name": "Jane Smith",
            "first_name": "Jane",
            "last_name": "Smith",
            "timezone": "America/Los_Angeles",
            "status": UserStatus.ACTIVE,
            "is_active": True,
            "is_verified": True,
            "verification_level": "basic",
            "max_bet_size": Decimal("500.00"),
            "daily_bet_limit": Decimal("2000.00"),
            "monthly_bet_limit": Decimal("20000.00"),
            "risk_tolerance": "medium",
            "auto_kelly_sizing": False,
            "max_kelly_fraction": 0.10,
            "preferred_sports": '["nfl"]',
            "notification_preferences": '{"email": true, "push": false, "sms": true}',
            "ui_preferences": '{"theme": "light", "currency": "USD"}',
        },
        {
            "external_id": "user_003_test",
            "email": "mike.wilson@example.com",
            "name": "Mike Wilson",
            "first_name": "Mike",
            "last_name": "Wilson",
            "timezone": "America/Chicago",
            "status": UserStatus.PENDING_VERIFICATION,
            "is_active": True,
            "is_verified": False,
            "verification_level": "basic",
            "max_bet_size": Decimal("100.00"),
            "daily_bet_limit": Decimal("500.00"),
            "monthly_bet_limit": Decimal("5000.00"),
            "risk_tolerance": "low",
            "auto_kelly_sizing": False,
            "max_kelly_fraction": 0.05,
            "preferred_sports": '["nfl", "mlb"]',
            "notification_preferences": '{"email": true, "push": true, "sms": false}',
            "ui_preferences": '{"theme": "auto", "currency": "USD"}',
        },
    ]

    created_users = []
    for user_data in sample_users:
        # Check if user already exists
        existing_user = user_crud.get_by_email(db=db, email=str(user_data["email"]))
        if not existing_user:
            db_user = User(**user_data)
            db.add(db_user)
            created_users.append(db_user)

    if created_users:
        db.commit()
        for user in created_users:
            db.refresh(user)

    return created_users


def create_sample_events(db: Session) -> List[Event]:
    """Create sample events for testing"""
    now = datetime.utcnow()
    next_week = now + timedelta(days=7)

    sample_events = [
        {
            "event_id": "nfl_2024_week_4_chiefs_chargers",
            "sport_key": "americanfootball_nfl",
            "commence_time": next_week,
            "home_team": "Los Angeles Chargers",
            "away_team": "Kansas City Chiefs",
            "season": 2024,
            "week": 4,
            "venue": "SoFi Stadium",
            "region": "us",
            "status": "scheduled",
        },
        {
            "event_id": "nfl_2024_week_4_bills_jets",
            "sport_key": "americanfootball_nfl",
            "commence_time": next_week + timedelta(hours=3),
            "home_team": "New York Jets",
            "away_team": "Buffalo Bills",
            "season": 2024,
            "week": 4,
            "venue": "MetLife Stadium",
            "region": "us",
            "status": "scheduled",
        },
    ]

    created_events = []
    for event_data in sample_events:
        # Check if event already exists
        existing_event = db.query(Event).filter(Event.event_id == event_data["event_id"]).first()
        if not existing_event:
            db_event = Event(**event_data)
            db.add(db_event)
            created_events.append(db_event)

    if created_events:
        db.commit()
        for event in created_events:
            db.refresh(event)

    return created_events


def create_sample_edges(db: Session) -> List[Edge]:
    """Create sample edges for testing"""
    # Ensure we have events first
    events = create_sample_events(db)
    if not events:
        events = db.query(Event).limit(2).all()

    if not events:
        raise ValueError("No events available for creating sample edges")

    sample_edges = [
        {
            "sport_key": "americanfootball_nfl",
            "event_id": events[0].event_id,
            "market_type": "player_props",
            "market_description": "Josh Allen Passing Yards",
            "player": "Josh Allen",
            "position": "QB",
            "line": 285.5,
            "side": "over",
            "best_odds_american": 105,
            "best_odds_decimal": 2.05,
            "best_sportsbook": "DraftKings",
            "implied_probability": 0.4878,
            "fair_probability": 0.52,
            "edge_percentage": 0.0656,
            "expected_value_per_dollar": 0.0656,
            "kelly_fraction": 0.1264,
            "model_probability": 0.52,
            "model_confidence": 0.85,
            "strategy_tag": "qb_yards_v2",
            "season": 2024,
            "week": 4,
            "team": "BUF",
            "opponent_team": "NYJ",
            "home_team": "New York Jets",
            "away_team": "Buffalo Bills",
            "is_home": False,
            "defense_tier": "generous",
            "defense_score": 2.3,
            "opponent_defense_code": "NYJ",
        },
        {
            "sport_key": "americanfootball_nfl",
            "event_id": events[0].event_id,
            "market_type": "player_props",
            "market_description": "Stefon Diggs Receiving Yards",
            "player": "Stefon Diggs",
            "position": "WR",
            "line": 75.5,
            "side": "over",
            "best_odds_american": -110,
            "best_odds_decimal": 1.91,
            "best_sportsbook": "FanDuel",
            "implied_probability": 0.5238,
            "fair_probability": 0.58,
            "edge_percentage": 0.1076,
            "expected_value_per_dollar": 0.1076,
            "kelly_fraction": 0.1983,
            "model_probability": 0.58,
            "model_confidence": 0.78,
            "strategy_tag": "wr_rec_yards_v1",
            "season": 2024,
            "week": 4,
            "team": "BUF",
            "opponent_team": "NYJ",
            "home_team": "New York Jets",
            "away_team": "Buffalo Bills",
            "is_home": False,
            "defense_tier": "stingy",
            "defense_score": -1.8,
            "opponent_defense_code": "NYJ",
        },
        {
            "sport_key": "americanfootball_nfl",
            "event_id": events[1].event_id if len(events) > 1 else events[0].event_id,
            "market_type": "totals",
            "market_description": "Total Points O/U",
            "line": 47.5,
            "side": "under",
            "best_odds_american": 110,
            "best_odds_decimal": 2.10,
            "best_sportsbook": "Caesars",
            "implied_probability": 0.4762,
            "fair_probability": 0.53,
            "edge_percentage": 0.1128,
            "expected_value_per_dollar": 0.1128,
            "kelly_fraction": 0.2055,
            "model_probability": 0.53,
            "model_confidence": 0.72,
            "strategy_tag": "game_totals_v1",
            "season": 2024,
            "week": 4,
            "home_team": "Los Angeles Chargers",
            "away_team": "Kansas City Chiefs",
        },
    ]

    created_edges = []
    for edge_data in sample_edges:
        # Check if similar edge already exists
        existing_edge = (
            db.query(Edge)
            .filter(
                Edge.event_id == edge_data["event_id"],
                Edge.market_type == edge_data["market_type"],
                Edge.player == edge_data.get("player"),
                Edge.side == edge_data["side"],
            )
            .first()
        )

        if not existing_edge:
            db_edge = Edge(**edge_data)
            db.add(db_edge)
            created_edges.append(db_edge)

    if created_edges:
        db.commit()
        for edge in created_edges:
            db.refresh(edge)

    return created_edges


def create_sample_bets(db: Session) -> List[Bet]:
    """Create sample bets for testing"""
    # Get sample users and edges
    users = db.query(User).filter(User.email.like("%@example.com")).limit(2).all()
    edges = db.query(Edge).limit(3).all()

    if not users:
        users = create_sample_users(db)
    if not edges:
        edges = create_sample_edges(db)

    if not users or not edges:
        raise ValueError("No users or edges available for creating sample bets")

    sample_bets = [
        {
            "user_id": users[0].id,
            "external_user_id": users[0].external_id,
            "event_id": edges[0].event_id,
            "edge_id": edges[0].edge_id,
            "market_type": edges[0].market_type,
            "market_description": edges[0].market_description,
            "selection": f"{edges[0].player} {edges[0].side} {edges[0].line}",
            "line": edges[0].line,
            "side": edges[0].side,
            "stake": Decimal("250.00"),
            "odds_american": edges[0].best_odds_american,
            "odds_decimal": edges[0].best_odds_decimal,
            "potential_return": Decimal("250.00") * Decimal(str(edges[0].best_odds_decimal)),
            "sportsbook_id": "draftkings",
            "sportsbook_name": "DraftKings",
            "external_bet_id": "DK_12345678",
            "edge_percentage": edges[0].edge_percentage,
            "kelly_fraction_used": edges[0].kelly_fraction,
            "expected_value": Decimal("250.00") * Decimal(str(edges[0].expected_value_per_dollar)),
            "model_probability": edges[0].model_probability,
            "notes": "Test bet from edge recommendation",
            "tags": '["recommended", "high_confidence"]',
            "source": "automated",
            "placed_at": datetime.utcnow() - timedelta(hours=2),
        },
        {
            "user_id": users[1].id if len(users) > 1 else users[0].id,
            "external_user_id": users[1].external_id if len(users) > 1 else users[0].external_id,
            "event_id": edges[1].event_id if len(edges) > 1 else edges[0].event_id,
            "edge_id": edges[1].edge_id if len(edges) > 1 else None,
            "market_type": "moneyline",
            "market_description": "Game Winner",
            "selection": "Buffalo Bills",
            "side": "away",
            "stake": Decimal("100.00"),
            "odds_american": -120,
            "odds_decimal": 1.83,
            "potential_return": Decimal("100.00") * Decimal("1.83"),
            "sportsbook_id": "fanduel",
            "sportsbook_name": "FanDuel",
            "external_bet_id": "FD_87654321",
            "notes": "Manual bet - gut feeling",
            "tags": '["manual", "moneyline"]',
            "source": "manual",
            "placed_at": datetime.utcnow() - timedelta(hours=5),
            "status": BetStatus.SETTLED,
            "result": "win",
            "settled_at": datetime.utcnow() - timedelta(hours=1),
            "actual_return": Decimal("183.00"),
            "net_profit": Decimal("83.00"),
        },
        {
            "user_id": users[0].id,
            "external_user_id": users[0].external_id,
            "event_id": edges[2].event_id if len(edges) > 2 else edges[0].event_id,
            "edge_id": edges[2].edge_id if len(edges) > 2 else None,
            "market_type": "totals",
            "market_description": "Total Points",
            "selection": "Under 47.5",
            "line": 47.5,
            "side": "under",
            "stake": Decimal("500.00"),
            "odds_american": 110,
            "odds_decimal": 2.10,
            "potential_return": Decimal("500.00") * Decimal("2.10"),
            "sportsbook_id": "caesars",
            "sportsbook_name": "Caesars Sportsbook",
            "notes": "High confidence edge",
            "tags": '["edge", "totals"]',
            "source": "automated",
            "placed_at": datetime.utcnow() - timedelta(minutes=30),
        },
    ]

    created_bets = []
    for bet_data in sample_bets:
        db_bet = Bet(**bet_data)
        db.add(db_bet)
        created_bets.append(db_bet)

    if created_bets:
        db.commit()
        for bet in created_bets:
            db.refresh(bet)

    return created_bets


def create_sample_transactions(db: Session) -> List[Transaction]:
    """Create sample transactions for testing"""
    # Get sample users
    users = db.query(User).filter(User.email.like("%@example.com")).limit(2).all()
    bets = db.query(Bet).limit(3).all()

    if not users:
        users = create_sample_users(db)
    if not bets:
        bets = create_sample_bets(db)

    sample_transactions = [
        # Initial deposit
        {
            "user_id": users[0].id,
            "amount": Decimal("5000.00"),
            "currency": "USD",
            "transaction_type": TransactionType.DEPOSIT,
            "status": TransactionStatus.COMPLETED,
            "sportsbook_id": "draftkings",
            "sportsbook_name": "DraftKings",
            "external_transaction_id": "DK_DEP_123456",
            "description": "Initial deposit",
            "reference": "DEP_001",
            "category": "account",
            "fee_amount": Decimal("0.00"),
            "net_amount": Decimal("5000.00"),
            "processed_at": datetime.utcnow() - timedelta(days=3),
        },
        # Bet placement
        {
            "user_id": users[0].id,
            "bet_id": bets[0].id if bets else None,
            "amount": Decimal("-250.00"),
            "currency": "USD",
            "transaction_type": TransactionType.BET_PLACED,
            "status": TransactionStatus.COMPLETED,
            "sportsbook_id": "draftkings",
            "sportsbook_name": "DraftKings",
            "external_transaction_id": "DK_BET_123456",
            "description": f"Bet placed: {bets[0].selection if bets else 'Sample bet'}",
            "reference": f"BET_{bets[0].id if bets else '001'}",
            "category": "betting",
            "fee_amount": Decimal("0.00"),
            "net_amount": Decimal("-250.00"),
            "processed_at": datetime.utcnow() - timedelta(hours=2),
        },
        # Winning bet payout
        {
            "user_id": users[1].id if len(users) > 1 else users[0].id,
            "bet_id": bets[1].id if len(bets) > 1 else None,
            "amount": Decimal("183.00"),
            "currency": "USD",
            "transaction_type": TransactionType.BET_PAYOUT,
            "status": TransactionStatus.COMPLETED,
            "sportsbook_id": "fanduel",
            "sportsbook_name": "FanDuel",
            "external_transaction_id": "FD_WIN_987654",
            "description": f"Winning bet payout: {bets[1].selection if len(bets) > 1 else 'Sample bet'}",
            "reference": f"WIN_{bets[1].id if len(bets) > 1 else '002'}",
            "category": "betting",
            "fee_amount": Decimal("0.00"),
            "net_amount": Decimal("183.00"),
            "processed_at": datetime.utcnow() - timedelta(hours=1),
        },
    ]

    created_transactions = []
    for transaction_data in sample_transactions:
        transaction_data = cast(Dict[str, Any], transaction_data)
        # Skip if bet_id is specified but bet doesn't exist
        if transaction_data.get("bet_id") and not bets:
            continue

        # Ensure all values are properly typed
        typed_transaction_data = {k: v for k, v in transaction_data.items()}
        db_transaction = Transaction(**typed_transaction_data)
        db.add(db_transaction)
        created_transactions.append(db_transaction)

    if created_transactions:
        db.commit()
        for transaction in created_transactions:
            db.refresh(transaction)

    return created_transactions


def load_sample_data(db: Session) -> Dict[str, List]:
    """Load all sample data for testing"""
    print("Creating sample users...")
    users = create_sample_users(db)

    print("Creating sample events...")
    events = create_sample_events(db)

    print("Creating sample edges...")
    edges = create_sample_edges(db)

    print("Creating sample bets...")
    bets = create_sample_bets(db)

    print("Creating sample transactions...")
    transactions = create_sample_transactions(db)

    print(f"Sample data created:")
    print(f"  - {len(users)} users")
    print(f"  - {len(events)} events")
    print(f"  - {len(edges)} edges")
    print(f"  - {len(bets)} bets")
    print(f"  - {len(transactions)} transactions")

    return {
        "users": users,
        "events": events,
        "edges": edges,
        "bets": bets,
        "transactions": transactions,
    }
