# Bet-That Database Models Documentation

## Overview

This document describes the comprehensive database schema for the Bet-That sports betting arbitrage platform. The schema is designed for scalability, data integrity, and comprehensive tracking of betting activities.

## Core Models

### 1. User Model

The `User` model handles user authentication, profiles, and risk management:

**Key Features:**

- Authentication fields (email, password_hash, verification)
- Profile information (name, timezone, contact info)
- Account status tracking (active, suspended, pending verification)
- Risk management (bet limits, Kelly fraction settings)
- User preferences (sports, notifications, UI settings)
- Audit trail and soft delete support

**Risk Management Fields:**

- `max_bet_size`: Maximum single bet amount
- `daily_bet_limit`: Daily betting limit
- `monthly_bet_limit`: Monthly betting limit
- `risk_tolerance`: User's risk preference (low/medium/high)
- `auto_kelly_sizing`: Enable automatic Kelly criterion sizing
- `max_kelly_fraction`: Maximum Kelly fraction (0-1)

```python
# Example usage
user = User(
    external_id="user_123",
    email="trader@example.com",
    max_bet_size=Decimal("1000.00"),
    risk_tolerance="medium",
    max_kelly_fraction=0.25
)
```

### 2. Edge Model

The `Edge` model represents arbitrage opportunities with comprehensive tracking:

**Key Features:**

- Market identification (sport, event, market type)
- Arbitrage data (odds, probabilities, edge percentage)
- Profitability metrics (expected value, Kelly fraction)
- Temporal tracking (discovery, expiration, updates)
- Model confidence and validation
- Context data (teams, defense ratings, matchups)

**Core Calculations:**

- `edge_percentage`: Advantage over implied probability
- `expected_value_per_dollar`: Expected return per dollar bet
- `kelly_fraction`: Optimal bet size using Kelly criterion
- `recommended_stake`: Calculated optimal stake amount

```python
# Example usage
edge = Edge(
    sport_key="americanfootball_nfl",
    event_id="chiefs_vs_chargers_2024_w4",
    market_type="player_props",
    player="Patrick Mahomes",
    line=285.5,
    side="over",
    best_odds_american=110,
    edge_percentage=0.0823,
    kelly_fraction=0.1546
)
```

### 3. Bet Model

The `Bet` model tracks all betting activity with comprehensive financial data:

**Key Features:**

- User and edge relationships
- Financial tracking (stake, odds, returns, profit)
- Status management (pending, settled, cancelled)
- Platform integration (sportsbook data, external IDs)
- CLV (Closing Line Value) tracking
- Risk metadata and audit trail

**Financial Fields:**

- `stake`: Amount wagered
- `odds_american/decimal`: Odds in both formats
- `potential_return`: Maximum possible return
- `actual_return`: Actual payout received
- `net_profit`: Profit/loss after stake

```python
# Example usage
bet = Bet(
    user_id=user.id,
    event_id="chiefs_vs_chargers_2024_w4",
    edge_id=edge.edge_id,
    market_type="player_props",
    stake=Decimal("250.00"),
    odds_american=110,
    sportsbook_id="draftkings",
    status=BetStatus.PENDING
)
```

### 4. Transaction Model

The `Transaction` model provides comprehensive financial record keeping:

**Key Features:**

- User and bet relationships
- Transaction types (deposits, withdrawals, bet payouts)
- Platform tracking (sportsbook integration)
- Processing status and retry logic
- Fee tracking and reconciliation
- Audit trail for compliance

**Transaction Types:**

- `DEPOSIT`: Money added to account
- `WITHDRAWAL`: Money withdrawn from account
- `BET_PLACED`: Bet placement (debit)
- `BET_PAYOUT`: Winning bet payout (credit)
- `BET_REFUND`: Bet refund/cancellation
- `BONUS`: Promotional credits
- `FEE`: Platform or processing fees

```python
# Example usage
transaction = Transaction(
    user_id=user.id,
    bet_id=bet.id,
    amount=Decimal("-250.00"),  # Negative for debits
    transaction_type=TransactionType.BET_PLACED,
    sportsbook_id="draftkings",
    status=TransactionStatus.COMPLETED
)
```

## Database Features

### Indexes and Performance

All models include comprehensive indexing for optimal query performance:

- **Composite indexes** for common query patterns
- **Foreign key indexes** for relationship queries
- **Status and timestamp indexes** for filtering
- **Descending indexes** for ranking queries (edge percentage, expected value)

### Data Integrity

- **Check constraints** validate data ranges and formats
- **Foreign key constraints** ensure referential integrity
- **Unique constraints** prevent duplicate data
- **NOT NULL constraints** enforce required fields

### Audit Trail

All models include comprehensive audit capabilities:

- `created_at`: Record creation timestamp
- `updated_at`: Last modification timestamp
- `created_by`: User who created the record
- Soft delete support with `deleted_at` field

### Soft Delete

Models support soft deletion for data retention and audit compliance:

```python
# Soft delete preserves data for audit
user.deleted_at = datetime.utcnow()

# Query automatically excludes soft-deleted records
active_users = user_crud.get_multi(db=db, limit=100)
```

## Relationships

The models form a comprehensive relationship graph:

```
User (1) ──── (N) Bet ──── (1) Edge
 │                 │
 │                 └── (N) Transaction
 │
 └── (N) Transaction

Event (1) ──── (N) Edge
 │
 └── (N) Bet
```

## API Schemas

Each model has corresponding Pydantic schemas for API serialization:

- **Create schemas**: For new record creation
- **Update schemas**: For partial updates
- **Response schemas**: For API responses
- **List schemas**: For paginated responses

## CRUD Operations

Comprehensive CRUD operations are provided for each model:

### Base Operations

- `get()`: Get by ID
- `get_multi()`: Get multiple with pagination
- `create()`: Create new record
- `update()`: Update existing record
- `remove()`: Soft delete record

### Specialized Operations

**User CRUD:**

- `get_by_email()`: Find by email
- `get_by_external_id()`: Find by external ID
- `verify_user()`: Complete user verification
- `suspend_user()`: Suspend account
- `get_user_statistics()`: Comprehensive stats

**Bet CRUD:**

- `create_with_user()`: Create bet with validation
- `get_by_user()`: Get user's bets
- `settle_bet()`: Settle with result
- `cancel_bet()`: Cancel pending bet
- `update_clv()`: Add CLV data
- `get_user_bet_statistics()`: Performance metrics

**Edge CRUD:**

- `get_active_edges()`: Current opportunities
- `get_top_edges()`: Best opportunities
- `search_edges()`: Advanced filtering
- `mark_stale()`: Mark as outdated
- `cleanup_expired_edges()`: Batch cleanup

**Transaction CRUD:**

- `create_with_user()`: Create with validation
- `complete_transaction()`: Mark as completed
- `fail_transaction()`: Handle failures
- `get_user_balance()`: Calculate balance
- `create_bet_transaction()`: Bet-related transactions

## Database Migration

### Current System

The project uses a hybrid migration approach:

1. **SQL Migration Files**: Located in `/migrations/`
   - `002_create_enhanced_user_models.sql`: Creates all new tables
   - Includes comprehensive indexes and constraints
   - SQLite-compatible with foreign key support

2. **SQLAlchemy Integration**: Models defined in `/api/models.py`
   - Type-safe model definitions
   - Automatic relationship handling
   - Validation and business logic

### Running Migrations

```bash
# Run the enhanced database migration
cd /Users/vato/work/Bet-That
python3 scripts/init_enhanced_db.py --migrate --sample-data

# Or run manually
sqlite3 storage/odds.db < migrations/002_create_enhanced_user_models.sql
```

### Sample Data

Load test data for development:

```python
from api.fixtures.sample_data import load_sample_data
from api.database import get_db_session

with get_db_session() as db:
    sample_data = load_sample_data(db)
```

## Performance Considerations

### Query Optimization

- Use `select_related`/`joinedload` for relationship queries
- Leverage composite indexes for complex filters
- Implement pagination for large result sets
- Use views for frequently accessed complex queries

### Database Tuning

SQLite configuration for production:

```sql
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;
PRAGMA synchronous=NORMAL;
PRAGMA cache_size=10000;
PRAGMA temp_store=memory;
```

### Monitoring

Built-in views for monitoring:

- `active_edges`: Current arbitrage opportunities
- `user_bet_stats`: User performance statistics
- `dashboard_summary`: System-wide metrics

## Security Considerations

### Data Protection

- Sensitive fields (password_hash) are properly secured
- Soft delete preserves audit trail
- User data isolation through proper foreign keys

### Validation

- Comprehensive check constraints prevent invalid data
- Pydantic schemas validate API inputs
- SQLAlchemy validators provide business logic validation

### Compliance

- Audit trail tracks all changes
- User verification levels support KYC requirements
- Transaction records enable regulatory reporting

## Usage Examples

### Creating a Complete Betting Flow

```python
from api.crud import user_crud, edge_crud, bet_crud, transaction_crud
from api.schemas import UserRegistrationRequest, BetCreateRequest, TransactionCreateRequest

# 1. Create user
user_data = UserRegistrationRequest(
    external_id="supabase_user_123",
    email="trader@example.com",
    name="Professional Trader"
)
user = user_crud.create(db=db, obj_in=user_data)

# 2. Create edge opportunity
edge_data = EdgeCreateRequest(
    sport_key="americanfootball_nfl",
    event_id="game_123",
    market_type="player_props",
    player="Josh Allen",
    line=285.5,
    side="over",
    best_odds_american=105,
    edge_percentage=0.0823,
    kelly_fraction=0.1546
)
edge = edge_crud.create(db=db, obj_in=edge_data)

# 3. Place bet
bet_data = BetCreateRequest(
    event_id=edge.event_id,
    edge_id=edge.edge_id,
    market_type=edge.market_type,
    stake=Decimal("250.00"),
    odds_american=105,
    sportsbook_id="draftkings"
)
bet = bet_crud.create_with_user(db=db, obj_in=bet_data, user_id=user.id)

# 4. Create bet placement transaction
transaction = transaction_crud.create_bet_transaction(
    db=db,
    bet_id=bet.id,
    transaction_type=TransactionType.BET_PLACED,
    amount=Decimal("-250.00"),
    sportsbook_id="draftkings"
)
```

## Migration Notes

### Breaking Changes

- Old `user_bets` table is replaced with enhanced `bets` table
- Additional fields added to `events` table
- New `edges` and `transactions` tables

### Data Migration

- Existing user data will be preserved
- Bet data structure has changed - manual migration may be needed
- Foreign key relationships are now enforced

### Testing

```bash
# Test the new models
python3 -m pytest tests/ -v

# Test with sample data
python3 scripts/init_enhanced_db.py --sample-data --log-level DEBUG
```

This enhanced schema provides a solid foundation for a professional sports betting arbitrage platform with proper data integrity, performance optimization, and comprehensive tracking capabilities.
