#!/usr/bin/env python3
"""Validate the enhanced database models"""

import sys
from decimal import Decimal
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from api.crud import bet_crud, edge_crud, transaction_crud, user_crud
from api.database import create_tables, get_db_session, init_database
from api.models import Bet, BetStatus, Edge, EdgeStatus, Event, Transaction, User, UserStatus
from api.schemas import BetCreateRequest, EdgeCreateRequest, UserRegistrationRequest


def test_model_creation():
    """Test that all models can be created successfully"""
    print("Testing model creation...")

    try:
        # Initialize database
        init_database()
        print("✓ Database initialized successfully")

        # Create tables
        create_tables()
        print("✓ Tables created successfully")

        with get_db_session() as db:
            # Test User creation
            user_data = UserRegistrationRequest(
                external_id="test_user_001",
                email="test@example.com",
                name="Test User",
                timezone="America/New_York",
            )
            user = user_crud.create(db=db, obj_in=user_data)
            print(f"✓ User created: {user.email} (ID: {user.id})")

            # Create a test event
            event = Event(
                event_id="test_event_001",
                sport_key="americanfootball_nfl",
                home_team="Test Home Team",
                away_team="Test Away Team",
                season=2024,
                week=4,
            )
            db.add(event)
            db.commit()
            db.refresh(event)
            print(f"✓ Event created: {event.event_id}")

            # Test Edge creation
            edge_data = EdgeCreateRequest(
                sport_key="americanfootball_nfl",
                event_id=event.event_id,
                market_type="player_props",
                market_description="Test Player Passing Yards",
                player="Test Player",
                line=250.5,
                side="over",
                best_odds_american=110,
                best_odds_decimal=2.10,
                best_sportsbook="test_book",
                implied_probability=0.4762,
                fair_probability=0.55,
                edge_percentage=0.1556,
                expected_value_per_dollar=0.1556,
                kelly_fraction=0.2911,
                model_probability=0.55,
                strategy_tag="test_strategy",
            )
            edge = edge_crud.create(db=db, obj_in=edge_data)
            print(f"✓ Edge created: {edge.market_description} (ID: {edge.edge_id})")

            # Test Bet creation
            bet_data = BetCreateRequest(
                event_id=event.event_id,
                edge_id=edge.edge_id,
                market_type="player_props",
                market_description="Test Player Passing Yards",
                selection="Test Player Over 250.5 Passing Yards",
                line=250.5,
                side="over",
                stake=Decimal("100.00"),
                odds_american=110,
                odds_decimal=2.10,
                sportsbook_id="test_book",
                sportsbook_name="Test Sportsbook",
            )
            bet = bet_crud.create_with_user(db=db, obj_in=bet_data, user_id=user.id)
            print(f"✓ Bet created: {bet.selection} (ID: {bet.id})")

            # Test Transaction creation
            from api.models import TransactionType
            from api.schemas import TransactionCreateRequest

            transaction_data = TransactionCreateRequest(
                amount=Decimal("-100.00"),
                transaction_type=TransactionType.BET_PLACED,
                bet_id=bet.id,
                sportsbook_id="test_book",
                description="Test bet placement",
                category="betting",
            )
            transaction = transaction_crud.create_with_user(
                db=db, obj_in=transaction_data, user_id=user.id
            )
            print(f"✓ Transaction created: {transaction.description} (ID: {transaction.id})")

            # Test relationships
            assert bet.user.email == user.email
            assert bet.edge.edge_id == edge.edge_id
            assert transaction.bet.id == bet.id
            assert transaction.user.id == user.id
            print("✓ Relationships working correctly")

            # Test model methods
            assert user.can_place_bet(500.0) == True
            assert user.can_place_bet(5000.0) == False
            assert bet.calculate_potential_return() > 0
            assert edge.calculate_recommended_stake(10000.0) > 0
            print("✓ Model methods working correctly")

            # Test CRUD operations
            user_stats = user_crud.get_user_statistics(db=db, user_id=user.id)
            bet_stats = bet_crud.get_user_bet_statistics(db=db, user_id=user.id)
            edge_stats = edge_crud.get_edge_statistics(db=db)

            assert user_stats is not None
            assert bet_stats is not None
            assert edge_stats is not None
            print("✓ Statistics methods working correctly")

        print("\n🎉 All model validations passed successfully!")
        print("\nNext steps:")
        print("1. Run the migration: python3 scripts/init_enhanced_db.py --migrate")
        print("2. Load sample data: python3 scripts/init_enhanced_db.py --sample-data")
        print("3. Start the API: uvicorn api.main:app --reload")

    except Exception as e:
        print(f"❌ Validation failed: {str(e)}")
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = test_model_creation()
    sys.exit(0 if success else 1)
