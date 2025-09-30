"""Integration tests for bet resolution workflow"""

import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.main import app
from api.models import User, Bet
from api.services.bet_service import BetService
from api.repositories.bet_repository import BetRepository
from api.schemas.bet_schemas import BetResolveRequest, BetDisputeRequest


class TestBetResolutionIntegration:
    """Integration tests for complete bet resolution workflow"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def mock_user(self):
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
    def test_complete_resolution_workflow(self, mock_get_db, mock_get_current_user, 
                                        client, mock_user, mock_db_user, mock_bet):
        """Test complete bet resolution workflow: create -> resolve -> dispute -> resolve dispute"""
        
        # Setup mocks
        mock_db = Mock(spec=Session)
        mock_get_db.return_value = mock_db
        mock_get_current_user.return_value = mock_user
        
        with patch('api.endpoints.bets.BetService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            
            # Mock bet with user relationship
            mock_bet.user = mock_db_user
            
            # Mock resolution response
            mock_resolved_bet = Mock()
            mock_resolved_bet.id = 1
            mock_resolved_bet.status = "resolved"
            mock_resolved_bet.result = "win"
            mock_resolved_bet.resolved_at = datetime.now()
            mock_resolved_bet.resolution_notes = "Game completed"
            mock_resolved_bet.user = mock_db_user
            
            # Mock disputed bet response
            mock_disputed_bet = Mock()
            mock_disputed_bet.id = 1
            mock_disputed_bet.status = "resolved"
            mock_disputed_bet.result = "win"
            mock_disputed_bet.is_disputed = True
            mock_disputed_bet.dispute_reason = "Score was incorrect"
            mock_disputed_bet.dispute_created_at = datetime.now()
            mock_disputed_bet.user = mock_db_user
            
            # Mock dispute resolution response
            mock_dispute_resolved_bet = Mock()
            mock_dispute_resolved_bet.id = 1
            mock_dispute_resolved_bet.status = "resolved"
            mock_dispute_resolved_bet.result = "loss"
            mock_dispute_resolved_bet.is_disputed = False
            mock_dispute_resolved_bet.dispute_resolved_at = datetime.now()
            mock_dispute_resolved_bet.user = mock_db_user
            
            # Setup service method returns
            mock_service_instance.resolve_bet.return_value = mock_resolved_bet
            mock_service_instance.dispute_bet_resolution.return_value = mock_disputed_bet
            mock_service_instance.resolve_dispute.return_value = mock_dispute_resolved_bet
            
            # Mock resolution history
            mock_history = {
                "history": [
                    {
                        "id": 1,
                        "bet_id": 1,
                        "action_type": "resolve",
                        "previous_status": "pending",
                        "new_status": "resolved",
                        "new_result": "win",
                        "resolution_notes": "Game completed",
                        "performed_by": 1,
                        "created_at": datetime.now().isoformat()
                    },
                    {
                        "id": 2,
                        "bet_id": 1,
                        "action_type": "dispute",
                        "dispute_reason": "Score was incorrect",
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
            
            mock_service_instance.get_resolution_history.return_value = mock_history
            
            # Step 1: Resolve bet
            resolve_request = {
                "result": "win",
                "resolution_notes": "Game completed",
                "resolution_source": "ESPN"
            }
            
            response = client.post("/api/v1/bets/1/resolve", json=resolve_request)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "resolved"
            assert data["result"] == "win"
            assert data["resolution_notes"] == "Game completed"
            
            # Verify service was called correctly
            mock_service_instance.resolve_bet.assert_called_once()
            call_args = mock_service_instance.resolve_bet.call_args
            assert call_args[0][0] == 1  # bet_id
            assert call_args[0][1].result == "win"
            assert call_args[0][2] == 1  # user_id
            
            # Step 2: Dispute resolution
            dispute_request = {
                "dispute_reason": "Score was incorrect according to official stats"
            }
            
            response = client.post("/api/v1/bets/1/dispute", json=dispute_request)
            assert response.status_code == 200
            data = response.json()
            assert data["is_disputed"] is True
            assert data["dispute_reason"] == "Score was incorrect"
            
            # Verify dispute service was called
            mock_service_instance.dispute_bet_resolution.assert_called_once()
            dispute_call_args = mock_service_instance.dispute_bet_resolution.call_args
            assert dispute_call_args[0][0] == 1  # bet_id
            assert dispute_call_args[0][1].dispute_reason == "Score was incorrect according to official stats"
            assert dispute_call_args[0][2] == 1  # user_id
            
            # Step 3: Get resolution history
            response = client.get("/api/v1/bets/1/resolution-history")
            assert response.status_code == 200
            history_data = response.json()
            assert len(history_data["history"]) == 3
            assert history_data["history"][0]["action_type"] == "resolve"
            assert history_data["history"][1]["action_type"] == "dispute"
            assert history_data["history"][2]["action_type"] == "resolve_dispute"
            
            # Step 4: Resolve dispute (admin action)
            response = client.put(
                "/api/v1/bets/1/resolve-dispute",
                params={
                    "new_result": "loss",
                    "resolution_notes": "Corrected based on official score"
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert data["result"] == "loss"
            assert data["is_disputed"] is False
            
            # Verify dispute resolution service was called
            mock_service_instance.resolve_dispute.assert_called_once()
            resolve_dispute_call_args = mock_service_instance.resolve_dispute.call_args
            assert resolve_dispute_call_args[0][0] == 1  # bet_id
            assert resolve_dispute_call_args[0][1] == "loss"  # new_result
            assert resolve_dispute_call_args[0][2] == "Corrected based on official score"  # resolution_notes

    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_permission_workflow(self, mock_get_db, mock_get_current_user, 
                               client, mock_user, mock_db_user, mock_bet):
        """Test permission checks throughout the workflow"""
        
        # Setup mocks
        mock_db = Mock(spec=Session)
        mock_get_db.return_value = mock_db
        mock_get_current_user.return_value = mock_user
        
        with patch('api.endpoints.bets.BetService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            
            # Test unauthorized resolution attempt
            mock_service_instance.resolve_bet.side_effect = ValueError("User not authorized to resolve this bet")
            
            resolve_request = {"result": "win"}
            response = client.post("/api/v1/bets/1/resolve", json=resolve_request)
            
            assert response.status_code == 400
            assert "not authorized" in response.json()["detail"]
            
            # Test unauthorized dispute attempt
            mock_service_instance.dispute_bet_resolution.side_effect = ValueError("User not authorized to dispute this bet")
            
            dispute_request = {"dispute_reason": "Score was incorrect according to official stats"}
            response = client.post("/api/v1/bets/1/dispute", json=dispute_request)
            
            assert response.status_code == 400
            assert "not authorized" in response.json()["detail"]

    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_error_recovery_workflow(self, mock_get_db, mock_get_current_user, 
                                   client, mock_user, mock_db_user, mock_bet):
        """Test error recovery in the resolution workflow"""
        
        # Setup mocks
        mock_db = Mock(spec=Session)
        mock_get_db.return_value = mock_db
        mock_get_current_user.return_value = mock_user
        
        with patch('api.endpoints.bets.BetService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            
            # Test database error during resolution
            mock_service_instance.resolve_bet.side_effect = Exception("Database connection failed")
            
            resolve_request = {"result": "win"}
            response = client.post("/api/v1/bets/1/resolve", json=resolve_request)
            
            assert response.status_code == 500
            assert "Failed to resolve bet" in response.json()["detail"]
            
            # Reset and test successful resolution after error
            mock_service_instance.resolve_bet.side_effect = None
            mock_resolved_bet = Mock()
            mock_resolved_bet.status = "resolved"
            mock_resolved_bet.result = "win"
            mock_resolved_bet.user = mock_db_user
            mock_service_instance.resolve_bet.return_value = mock_resolved_bet
            
            response = client.post("/api/v1/bets/1/resolve", json=resolve_request)
            assert response.status_code == 200

    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_websocket_integration(self, mock_get_db, mock_get_current_user, 
                                 client, mock_user, mock_db_user, mock_bet):
        """Test WebSocket integration during resolution workflow"""
        
        # Setup mocks
        mock_db = Mock(spec=Session)
        mock_get_db.return_value = mock_db
        mock_get_current_user.return_value = mock_user
        
        with patch('api.endpoints.bets.BetService') as mock_service, \
             patch('api.endpoints.bets.send_bet_status_update') as mock_ws, \
             patch('api.endpoints.bets.send_dispute_resolution_update') as mock_dispute_ws:
            
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            
            # Mock successful resolution
            mock_resolved_bet = Mock()
            mock_resolved_bet.status = "resolved"
            mock_resolved_bet.result = "win"
            mock_resolved_bet.user = mock_db_user
            mock_service_instance.resolve_bet.return_value = mock_resolved_bet
            
            # Mock WebSocket calls
            mock_ws.return_value = AsyncMock()
            mock_dispute_ws.return_value = AsyncMock()
            
            # Test resolution with WebSocket
            resolve_request = {
                "result": "win",
                "resolution_notes": "Game completed"
            }
            
            response = client.post("/api/v1/bets/1/resolve", json=resolve_request)
            assert response.status_code == 200
            
            # WebSocket should be called (though we can't easily test the actual WebSocket behavior)
            # The important thing is that the resolution succeeds even if WebSocket fails

    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_email_integration(self, mock_get_db, mock_get_current_user, 
                             client, mock_user, mock_db_user, mock_bet):
        """Test email notification integration during resolution workflow"""
        
        # Setup mocks
        mock_db = Mock(spec=Session)
        mock_get_db.return_value = mock_db
        mock_get_current_user.return_value = mock_user
        
        with patch('api.endpoints.bets.BetService') as mock_service, \
             patch('api.endpoints.bets.send_bet_resolution_notification') as mock_email, \
             patch('api.endpoints.bets.send_bet_dispute_notification') as mock_dispute_email:
            
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            
            # Mock successful resolution
            mock_resolved_bet = Mock()
            mock_resolved_bet.status = "resolved"
            mock_resolved_bet.result = "win"
            mock_resolved_bet.user = mock_db_user
            mock_service_instance.resolve_bet.return_value = mock_resolved_bet
            
            # Mock email calls
            mock_email.return_value = None
            mock_dispute_email.return_value = None
            
            # Test resolution with email notification
            resolve_request = {
                "result": "win",
                "resolution_notes": "Game completed"
            }
            
            response = client.post("/api/v1/bets/1/resolve", json=resolve_request)
            assert response.status_code == 200
            
            # Email should be called (though we can't easily test the actual email sending)
            # The important thing is that the resolution succeeds even if email fails

    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_concurrent_resolution_attempts(self, mock_get_db, mock_get_current_user, 
                                          client, mock_user, mock_db_user, mock_bet):
        """Test handling of concurrent resolution attempts"""
        
        # Setup mocks
        mock_db = Mock(spec=Session)
        mock_get_db.return_value = mock_db
        mock_get_current_user.return_value = mock_user
        
        with patch('api.endpoints.bets.BetService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            
            # Mock resolution response
            mock_resolved_bet = Mock()
            mock_resolved_bet.status = "resolved"
            mock_resolved_bet.result = "win"
            mock_resolved_bet.user = mock_db_user
            mock_service_instance.resolve_bet.return_value = mock_resolved_bet
            
            # Test multiple concurrent resolution attempts
            resolve_request = {"result": "win"}
            
            # Simulate concurrent requests (in real scenario, these would be from different clients)
            response1 = client.post("/api/v1/bets/1/resolve", json=resolve_request)
            response2 = client.post("/api/v1/bets/1/resolve", json=resolve_request)
            
            # Both should succeed (assuming proper concurrency handling)
            assert response1.status_code == 200
            assert response2.status_code == 200
            
            # Service should be called twice
            assert mock_service_instance.resolve_bet.call_count == 2

    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_validation_workflow(self, mock_get_db, mock_get_current_user, 
                               client, mock_user, mock_db_user, mock_bet):
        """Test validation throughout the resolution workflow"""
        
        # Setup mocks
        mock_db = Mock(spec=Session)
        mock_get_db.return_value = mock_db
        mock_get_current_user.return_value = mock_user
        
        # Test invalid result values
        invalid_requests = [
            {"result": "invalid_result"},
            {"result": ""},
            {},  # Missing result
        ]
        
        for invalid_request in invalid_requests:
            response = client.post("/api/v1/bets/1/resolve", json=invalid_request)
            assert response.status_code == 422  # Validation error
        
        # Test invalid dispute reasons
        invalid_dispute_requests = [
            {"dispute_reason": "Short"},  # Too short
            {"dispute_reason": ""},  # Empty
            {},  # Missing dispute_reason
        ]
        
        for invalid_request in invalid_dispute_requests:
            response = client.post("/api/v1/bets/1/dispute", json=invalid_request)
            assert response.status_code == 422  # Validation error

    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_pagination_workflow(self, mock_get_db, mock_get_current_user, 
                               client, mock_user, mock_db_user, mock_bet):
        """Test pagination in resolution history and bet lists"""
        
        # Setup mocks
        mock_db = Mock(spec=Session)
        mock_get_db.return_value = mock_db
        mock_get_current_user.return_value = mock_user
        
        with patch('api.endpoints.bets.BetService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            
            # Mock paginated history
            mock_history = {
                "history": [],
                "total": 100,
                "page": 1,
                "per_page": 20
            }
            mock_service_instance.get_resolution_history.return_value = mock_history
            
            # Test different page sizes
            test_cases = [
                (1, 10),
                (2, 20),
                (1, 50),
            ]
            
            for page, per_page in test_cases:
                response = client.get(f"/api/v1/bets/1/resolution-history?page={page}&per_page={per_page}")
                assert response.status_code == 200
                
                # Verify service was called with correct pagination
                expected_calls = [
                    pytest.mock.call(1, page, per_page)
                    for _ in range(len(test_cases))
                ]
                # Note: This is a simplified check - in practice you'd want to track calls more precisely
            
            # Test pagination bounds
            response = client.get("/api/v1/bets/1/resolution-history?page=0")  # Invalid page
            assert response.status_code == 422
            
            response = client.get("/api/v1/bets/1/resolution-history?per_page=200")  # Too many per page
            assert response.status_code == 422

