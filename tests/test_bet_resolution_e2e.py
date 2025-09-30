"""End-to-end tests for bet resolution workflow"""

import pytest
import asyncio
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient

from api.main import app
from api.models import User, Bet


class TestBetResolutionEndToEnd:
    """End-to-end tests for complete bet resolution workflow"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def mock_user_data(self):
        return {
            "external_id": "test_user_123",
            "email": "test@example.com",
            "name": "Test User"
        }
    
    @pytest.fixture
    def mock_db_user(self):
        return User(
            id=1,
            external_id="test_user_123",
            email="test@example.com",
            name="Test User",
            status="active",
            is_active=True,
            created_at=datetime.now()
        )
    
    @pytest.fixture
    def mock_bet_data(self):
        return {
            "event_id": "game_123",
            "market_type": "spread",
            "market_description": "Point Spread",
            "selection": "Home Team",
            "line": -3.5,
            "side": "home",
            "stake": 100.00,
            "odds_american": -110,
            "odds_decimal": 1.91,
            "sportsbook_id": "draftkings",
            "sportsbook_name": "DraftKings",
            "external_bet_id": "dk_123",
            "notes": "Test bet for E2E testing"
        }
    
    @pytest.fixture
    def mock_bet(self):
        return Bet(
            id=1,
            user_id=1,
            external_user_id="test_user_123",
            event_id="game_123",
            market_type="spread",
            market_description="Point Spread",
            selection="Home Team",
            line=-3.5,
            side="home",
            stake=Decimal("100.00"),
            odds_american=-110,
            odds_decimal=1.91,
            potential_return=Decimal("190.91"),
            status="pending",
            result=None,
            sportsbook_id="draftkings",
            sportsbook_name="DraftKings",
            external_bet_id="dk_123",
            source="manual",
            placed_at=datetime.now(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            resolved_at=None,
            resolved_by=None,
            resolution_notes=None,
            resolution_source=None,
            is_disputed=False,
            dispute_reason=None,
            dispute_created_at=None,
            dispute_resolved_at=None,
            dispute_resolved_by=None
        )

    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_complete_bet_lifecycle(self, mock_get_db, mock_get_current_user, 
                                  client, mock_user_data, mock_db_user, mock_bet_data, mock_bet):
        """Test complete bet lifecycle: create -> resolve -> verify updates"""
        
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_get_current_user.return_value = mock_user_data
        
        with patch('api.endpoints.bets.BetService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            
            # Step 1: Create a bet
            mock_created_bet = Mock()
            mock_created_bet.id = 1
            mock_created_bet.status = "pending"
            mock_created_bet.user_id = 1
            mock_created_bet.external_user_id = "test_user_123"
            mock_created_bet.event_id = "game_123"
            mock_created_bet.market_type = "spread"
            mock_created_bet.market_description = "Point Spread"
            mock_created_bet.selection = "Home Team"
            mock_created_bet.line = -3.5
            mock_created_bet.side = "home"
            mock_created_bet.stake = Decimal("100.00")
            mock_created_bet.odds_american = -110
            mock_created_bet.odds_decimal = 1.91
            mock_created_bet.potential_return = Decimal("190.91")
            mock_created_bet.sportsbook_name = "DraftKings"
            mock_created_bet.external_bet_id = "dk_123"
            mock_created_bet.notes = "Test bet for E2E testing"
            mock_created_bet.placed_at = datetime.now()
            mock_created_bet.created_at = datetime.now()
            mock_created_bet.updated_at = datetime.now()
            mock_created_bet.resolved_at = None
            mock_created_bet.resolved_by = None
            mock_created_bet.resolution_notes = None
            mock_created_bet.resolution_source = None
            mock_created_bet.is_disputed = False
            mock_created_bet.dispute_reason = None
            mock_created_bet.dispute_created_at = None
            mock_created_bet.dispute_resolved_at = None
            mock_created_bet.dispute_resolved_by = None
            
            # Mock user creation/lookup
            mock_db.query.return_value.filter.return_value.first.return_value = mock_db_user
            mock_db.add.return_value = None
            mock_db.commit.return_value = None
            mock_db.refresh.return_value = None
            
            # Create bet
            create_response = client.post("/api/v1/bets", json=mock_bet_data)
            assert create_response.status_code == 200
            
            created_bet_data = create_response.json()
            assert created_bet_data["status"] == "pending"
            assert created_bet_data["selection"] == "Home Team"
            assert created_bet_data["stake"] == 100.00
            
            # Step 2: Resolve the bet
            mock_resolved_bet = Mock()
            mock_resolved_bet.id = 1
            mock_resolved_bet.status = "resolved"
            mock_resolved_bet.result = "win"
            mock_resolved_bet.resolved_at = datetime.now()
            mock_resolved_bet.resolved_by = 1
            mock_resolved_bet.resolution_notes = "Game completed successfully"
            mock_resolved_bet.resolution_source = "ESPN"
            mock_resolved_bet.user = mock_db_user
            mock_resolved_bet.user_id = 1
            mock_resolved_bet.external_user_id = "test_user_123"
            mock_resolved_bet.event_id = "game_123"
            mock_resolved_bet.market_type = "spread"
            mock_resolved_bet.market_description = "Point Spread"
            mock_resolved_bet.selection = "Home Team"
            mock_resolved_bet.line = -3.5
            mock_resolved_bet.side = "home"
            mock_resolved_bet.stake = Decimal("100.00")
            mock_resolved_bet.odds_american = -110
            mock_resolved_bet.odds_decimal = 1.91
            mock_resolved_bet.potential_return = Decimal("190.91")
            mock_resolved_bet.sportsbook_name = "DraftKings"
            mock_resolved_bet.external_bet_id = "dk_123"
            mock_resolved_bet.notes = "Test bet for E2E testing"
            mock_resolved_bet.placed_at = datetime.now()
            mock_resolved_bet.created_at = datetime.now()
            mock_resolved_bet.updated_at = datetime.now()
            mock_resolved_bet.is_disputed = False
            mock_resolved_bet.dispute_reason = None
            mock_resolved_bet.dispute_created_at = None
            mock_resolved_bet.dispute_resolved_at = None
            mock_resolved_bet.dispute_resolved_by = None
            
            mock_service_instance.resolve_bet.return_value = mock_resolved_bet
            
            resolve_request = {
                "result": "win",
                "resolution_notes": "Game completed successfully",
                "resolution_source": "ESPN"
            }
            
            resolve_response = client.post("/api/v1/bets/1/resolve", json=resolve_request)
            assert resolve_response.status_code == 200
            
            resolved_bet_data = resolve_response.json()
            assert resolved_bet_data["status"] == "resolved"
            assert resolved_bet_data["result"] == "win"
            assert resolved_bet_data["resolution_notes"] == "Game completed successfully"
            assert resolved_bet_data["resolution_source"] == "ESPN"
            
            # Step 3: Verify bet appears in user's bet list
            mock_bet_list = {
                "bets": [resolved_bet_data],
                "total": 1,
                "page": 1,
                "per_page": 50
            }
            
            # Mock the get user bets endpoint
            bets_response = client.get("/api/v1/bets")
            assert bets_response.status_code == 200
            
            # Step 4: Get resolution history
            mock_history = {
                "history": [
                    {
                        "id": 1,
                        "bet_id": 1,
                        "action_type": "resolve",
                        "previous_status": "pending",
                        "new_status": "resolved",
                        "previous_result": None,
                        "new_result": "win",
                        "resolution_notes": "Game completed successfully",
                        "resolution_source": "ESPN",
                        "dispute_reason": None,
                        "performed_by": 1,
                        "created_at": datetime.now().isoformat()
                    }
                ],
                "total": 1,
                "page": 1,
                "per_page": 50
            }
            
            mock_service_instance.get_resolution_history.return_value = mock_history
            
            history_response = client.get("/api/v1/bets/1/resolution-history")
            assert history_response.status_code == 200
            
            history_data = history_response.json()
            assert len(history_data["history"]) == 1
            assert history_data["history"][0]["action_type"] == "resolve"
            assert history_data["history"][0]["new_result"] == "win"
            
            # Step 5: Verify WebSocket and email notifications were triggered
            # (These are tested in the service layer, but we verify the flow)
            mock_service_instance.resolve_bet.assert_called_once()

    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_dispute_workflow_e2e(self, mock_get_db, mock_get_current_user, 
                                client, mock_user_data, mock_db_user, mock_bet):
        """Test complete dispute workflow: resolve -> dispute -> resolve dispute"""
        
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_get_current_user.return_value = mock_user_data
        
        with patch('api.endpoints.bets.BetService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            
            # Step 1: Resolve bet
            mock_resolved_bet = Mock()
            mock_resolved_bet.id = 1
            mock_resolved_bet.status = "resolved"
            mock_resolved_bet.result = "win"
            mock_resolved_bet.resolved_at = datetime.now()
            mock_resolved_bet.resolved_by = 1
            mock_resolved_bet.resolution_notes = "Game completed"
            mock_resolved_bet.user = mock_db_user
            mock_resolved_bet.user_id = 1
            mock_resolved_bet.external_user_id = "test_user_123"
            mock_resolved_bet.event_id = "game_123"
            mock_resolved_bet.market_type = "spread"
            mock_resolved_bet.market_description = "Point Spread"
            mock_resolved_bet.selection = "Home Team"
            mock_resolved_bet.line = -3.5
            mock_resolved_bet.side = "home"
            mock_resolved_bet.stake = Decimal("100.00")
            mock_resolved_bet.odds_american = -110
            mock_resolved_bet.odds_decimal = 1.91
            mock_resolved_bet.potential_return = Decimal("190.91")
            mock_resolved_bet.sportsbook_name = "DraftKings"
            mock_resolved_bet.external_bet_id = "dk_123"
            mock_resolved_bet.placed_at = datetime.now()
            mock_resolved_bet.created_at = datetime.now()
            mock_resolved_bet.updated_at = datetime.now()
            mock_resolved_bet.is_disputed = False
            mock_resolved_bet.dispute_reason = None
            mock_resolved_bet.dispute_created_at = None
            mock_resolved_bet.dispute_resolved_at = None
            mock_resolved_bet.dispute_resolved_by = None
            
            mock_service_instance.resolve_bet.return_value = mock_resolved_bet
            
            resolve_request = {
                "result": "win",
                "resolution_notes": "Game completed"
            }
            
            resolve_response = client.post("/api/v1/bets/1/resolve", json=resolve_request)
            assert resolve_response.status_code == 200
            
            # Step 2: Dispute the resolution
            mock_disputed_bet = Mock()
            mock_disputed_bet.id = 1
            mock_disputed_bet.status = "resolved"
            mock_disputed_bet.result = "win"
            mock_disputed_bet.resolved_at = datetime.now()
            mock_disputed_bet.resolved_by = 1
            mock_disputed_bet.resolution_notes = "Game completed"
            mock_disputed_bet.is_disputed = True
            mock_disputed_bet.dispute_reason = "Score was incorrect according to official stats"
            mock_disputed_bet.dispute_created_at = datetime.now()
            mock_disputed_bet.user = mock_db_user
            mock_disputed_bet.user_id = 1
            mock_disputed_bet.external_user_id = "test_user_123"
            mock_disputed_bet.event_id = "game_123"
            mock_disputed_bet.market_type = "spread"
            mock_disputed_bet.market_description = "Point Spread"
            mock_disputed_bet.selection = "Home Team"
            mock_disputed_bet.line = -3.5
            mock_disputed_bet.side = "home"
            mock_disputed_bet.stake = Decimal("100.00")
            mock_disputed_bet.odds_american = -110
            mock_disputed_bet.odds_decimal = 1.91
            mock_disputed_bet.potential_return = Decimal("190.91")
            mock_disputed_bet.sportsbook_name = "DraftKings"
            mock_disputed_bet.external_bet_id = "dk_123"
            mock_disputed_bet.placed_at = datetime.now()
            mock_disputed_bet.created_at = datetime.now()
            mock_disputed_bet.updated_at = datetime.now()
            mock_disputed_bet.dispute_resolved_at = None
            mock_disputed_bet.dispute_resolved_by = None
            
            mock_service_instance.dispute_bet_resolution.return_value = mock_disputed_bet
            
            dispute_request = {
                "dispute_reason": "Score was incorrect according to official stats"
            }
            
            dispute_response = client.post("/api/v1/bets/1/dispute", json=dispute_request)
            assert dispute_response.status_code == 200
            
            disputed_bet_data = dispute_response.json()
            assert disputed_bet_data["is_disputed"] is True
            assert disputed_bet_data["dispute_reason"] == "Score was incorrect according to official stats"
            
            # Step 3: Resolve the dispute (admin action)
            mock_dispute_resolved_bet = Mock()
            mock_dispute_resolved_bet.id = 1
            mock_dispute_resolved_bet.status = "resolved"
            mock_dispute_resolved_bet.result = "loss"
            mock_dispute_resolved_bet.resolved_at = datetime.now()
            mock_dispute_resolved_bet.resolved_by = 1
            mock_dispute_resolved_bet.resolution_notes = "Corrected based on official score"
            mock_dispute_resolved_bet.is_disputed = False
            mock_dispute_resolved_bet.dispute_reason = "Score was incorrect according to official stats"
            mock_disputed_bet.dispute_created_at = datetime.now()
            mock_dispute_resolved_bet.dispute_resolved_at = datetime.now()
            mock_dispute_resolved_bet.dispute_resolved_by = 2
            mock_dispute_resolved_bet.user = mock_db_user
            mock_dispute_resolved_bet.user_id = 1
            mock_dispute_resolved_bet.external_user_id = "test_user_123"
            mock_dispute_resolved_bet.event_id = "game_123"
            mock_dispute_resolved_bet.market_type = "spread"
            mock_dispute_resolved_bet.market_description = "Point Spread"
            mock_dispute_resolved_bet.selection = "Home Team"
            mock_dispute_resolved_bet.line = -3.5
            mock_dispute_resolved_bet.side = "home"
            mock_dispute_resolved_bet.stake = Decimal("100.00")
            mock_dispute_resolved_bet.odds_american = -110
            mock_dispute_resolved_bet.odds_decimal = 1.91
            mock_dispute_resolved_bet.potential_return = Decimal("190.91")
            mock_dispute_resolved_bet.sportsbook_name = "DraftKings"
            mock_dispute_resolved_bet.external_bet_id = "dk_123"
            mock_dispute_resolved_bet.placed_at = datetime.now()
            mock_dispute_resolved_bet.created_at = datetime.now()
            mock_dispute_resolved_bet.updated_at = datetime.now()
            
            mock_service_instance.resolve_dispute.return_value = mock_dispute_resolved_bet
            
            resolve_dispute_response = client.put(
                "/api/v1/bets/1/resolve-dispute",
                params={
                    "new_result": "loss",
                    "resolution_notes": "Corrected based on official score"
                }
            )
            assert resolve_dispute_response.status_code == 200
            
            dispute_resolved_data = resolve_dispute_response.json()
            assert dispute_resolved_data["result"] == "loss"
            assert dispute_resolved_data["is_disputed"] is False
            
            # Step 4: Verify complete history
            mock_complete_history = {
                "history": [
                    {
                        "id": 1,
                        "bet_id": 1,
                        "action_type": "resolve",
                        "previous_status": "pending",
                        "new_status": "resolved",
                        "previous_result": None,
                        "new_result": "win",
                        "resolution_notes": "Game completed",
                        "performed_by": 1,
                        "created_at": datetime.now().isoformat()
                    },
                    {
                        "id": 2,
                        "bet_id": 1,
                        "action_type": "dispute",
                        "dispute_reason": "Score was incorrect according to official stats",
                        "performed_by": 1,
                        "created_at": datetime.now().isoformat()
                    },
                    {
                        "id": 3,
                        "bet_id": 1,
                        "action_type": "resolve_dispute",
                        "previous_result": "win",
                        "new_result": "loss",
                        "resolution_notes": "Corrected based on official score",
                        "performed_by": 2,
                        "created_at": datetime.now().isoformat()
                    }
                ],
                "total": 3,
                "page": 1,
                "per_page": 50
            }
            
            mock_service_instance.get_resolution_history.return_value = mock_complete_history
            
            history_response = client.get("/api/v1/bets/1/resolution-history")
            assert history_response.status_code == 200
            
            history_data = history_response.json()
            assert len(history_data["history"]) == 3
            assert history_data["history"][0]["action_type"] == "resolve"
            assert history_data["history"][1]["action_type"] == "dispute"
            assert history_data["history"][2]["action_type"] == "resolve_dispute"

    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_concurrent_user_workflow(self, mock_get_db, mock_get_current_user, 
                                    client, mock_user_data, mock_db_user, mock_bet):
        """Test concurrent users resolving different bets"""
        
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_get_current_user.return_value = mock_user_data
        
        with patch('api.endpoints.bets.BetService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            
            # Mock resolution for multiple bets
            mock_resolved_bet_1 = Mock()
            mock_resolved_bet_1.id = 1
            mock_resolved_bet_1.status = "resolved"
            mock_resolved_bet_1.result = "win"
            mock_resolved_bet_1.user = mock_db_user
            
            mock_resolved_bet_2 = Mock()
            mock_resolved_bet_2.id = 2
            mock_resolved_bet_2.status = "resolved"
            mock_resolved_bet_2.result = "loss"
            mock_resolved_bet_2.user = mock_db_user
            
            # Set up service to return different results based on bet ID
            def resolve_side_effect(bet_id, request, user_id):
                if bet_id == 1:
                    return mock_resolved_bet_1
                elif bet_id == 2:
                    return mock_resolved_bet_2
                else:
                    raise ValueError("Bet not found")
            
            mock_service_instance.resolve_bet.side_effect = resolve_side_effect
            
            # Resolve multiple bets concurrently
            resolve_requests = [
                {"bet_id": 1, "result": "win", "resolution_notes": "Game 1 completed"},
                {"bet_id": 2, "result": "loss", "resolution_notes": "Game 2 completed"}
            ]
            
            responses = []
            for req in resolve_requests:
                response = client.post(f"/api/v1/bets/{req['bet_id']}/resolve", 
                                     json={"result": req["result"], "resolution_notes": req["resolution_notes"]})
                responses.append(response)
            
            # Verify all resolutions succeeded
            for response in responses:
                assert response.status_code == 200
            
            # Verify service was called for each bet
            assert mock_service_instance.resolve_bet.call_count == 2

    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_error_recovery_workflow(self, mock_get_db, mock_get_current_user, 
                                   client, mock_user_data, mock_db_user, mock_bet):
        """Test error recovery in the workflow"""
        
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_get_current_user.return_value = mock_user_data
        
        with patch('api.endpoints.bets.BetService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            
            # Step 1: First resolution attempt fails
            mock_service_instance.resolve_bet.side_effect = Exception("Database connection failed")
            
            resolve_request = {"result": "win"}
            response = client.post("/api/v1/bets/1/resolve", json=resolve_request)
            
            assert response.status_code == 500
            assert "Failed to resolve bet" in response.json()["detail"]
            
            # Step 2: Retry resolution succeeds
            mock_resolved_bet = Mock()
            mock_resolved_bet.status = "resolved"
            mock_resolved_bet.result = "win"
            mock_resolved_bet.user = mock_db_user
            mock_resolved_bet.id = 1
            mock_resolved_bet.user_id = 1
            mock_resolved_bet.external_user_id = "test_user_123"
            mock_resolved_bet.event_id = "game_123"
            mock_resolved_bet.market_type = "spread"
            mock_resolved_bet.market_description = "Point Spread"
            mock_resolved_bet.selection = "Home Team"
            mock_resolved_bet.line = -3.5
            mock_resolved_bet.side = "home"
            mock_resolved_bet.stake = Decimal("100.00")
            mock_resolved_bet.odds_american = -110
            mock_resolved_bet.odds_decimal = 1.91
            mock_resolved_bet.potential_return = Decimal("190.91")
            mock_resolved_bet.sportsbook_name = "DraftKings"
            mock_resolved_bet.external_bet_id = "dk_123"
            mock_resolved_bet.placed_at = datetime.now()
            mock_resolved_bet.created_at = datetime.now()
            mock_resolved_bet.updated_at = datetime.now()
            mock_resolved_bet.resolved_at = datetime.now()
            mock_resolved_bet.resolved_by = 1
            mock_resolved_bet.resolution_notes = "Game completed"
            mock_resolved_bet.resolution_source = None
            mock_resolved_bet.is_disputed = False
            mock_resolved_bet.dispute_reason = None
            mock_resolved_bet.dispute_created_at = None
            mock_resolved_bet.dispute_resolved_at = None
            mock_resolved_bet.dispute_resolved_by = None
            
            mock_service_instance.resolve_bet.side_effect = None
            mock_service_instance.resolve_bet.return_value = mock_resolved_bet
            
            response = client.post("/api/v1/bets/1/resolve", json=resolve_request)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "resolved"
            assert data["result"] == "win"

    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_performance_workflow(self, mock_get_db, mock_get_current_user, 
                                client, mock_user_data, mock_db_user, mock_bet):
        """Test performance with multiple operations"""
        
        # Setup mocks
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        mock_get_current_user.return_value = mock_user_data
        
        with patch('api.endpoints.bets.BetService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            
            # Mock fast resolution
            mock_resolved_bet = Mock()
            mock_resolved_bet.status = "resolved"
            mock_resolved_bet.result = "win"
            mock_resolved_bet.user = mock_db_user
            mock_resolved_bet.id = 1
            mock_resolved_bet.user_id = 1
            mock_resolved_bet.external_user_id = "test_user_123"
            mock_resolved_bet.event_id = "game_123"
            mock_resolved_bet.market_type = "spread"
            mock_resolved_bet.market_description = "Point Spread"
            mock_resolved_bet.selection = "Home Team"
            mock_resolved_bet.line = -3.5
            mock_resolved_bet.side = "home"
            mock_resolved_bet.stake = Decimal("100.00")
            mock_resolved_bet.odds_american = -110
            mock_resolved_bet.odds_decimal = 1.91
            mock_resolved_bet.potential_return = Decimal("190.91")
            mock_resolved_bet.sportsbook_name = "DraftKings"
            mock_resolved_bet.external_bet_id = "dk_123"
            mock_resolved_bet.placed_at = datetime.now()
            mock_resolved_bet.created_at = datetime.now()
            mock_resolved_bet.updated_at = datetime.now()
            mock_resolved_bet.resolved_at = datetime.now()
            mock_resolved_bet.resolved_by = 1
            mock_resolved_bet.resolution_notes = "Game completed"
            mock_resolved_bet.resolution_source = None
            mock_resolved_bet.is_disputed = False
            mock_resolved_bet.dispute_reason = None
            mock_resolved_bet.dispute_created_at = None
            mock_resolved_bet.dispute_resolved_at = None
            mock_resolved_bet.dispute_resolved_by = None
            
            mock_service_instance.resolve_bet.return_value = mock_resolved_bet
            
            # Mock history response
            mock_history = {
                "history": [],
                "total": 0,
                "page": 1,
                "per_page": 50
            }
            mock_service_instance.get_resolution_history.return_value = mock_history
            
            # Perform multiple operations
            operations = [
                {"method": "POST", "url": "/api/v1/bets/1/resolve", "data": {"result": "win"}},
                {"method": "GET", "url": "/api/v1/bets/1/resolution-history", "data": None},
                {"method": "GET", "url": "/api/v1/bets", "data": None},
                {"method": "GET", "url": "/api/v1/bets/pending-resolution", "data": None}
            ]
            
            responses = []
            for op in operations:
                if op["method"] == "POST":
                    response = client.post(op["url"], json=op["data"])
                else:
                    response = client.get(op["url"])
                responses.append(response)
            
            # Verify all operations completed successfully
            for response in responses:
                assert response.status_code == 200
            
            # Verify service was called appropriately
            assert mock_service_instance.resolve_bet.call_count >= 1

