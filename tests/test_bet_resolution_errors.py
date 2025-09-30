"""Error handling tests for bet resolution functionality"""

import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import Session

from api.main import app
from api.models import User, Bet
from api.services.bet_service import BetService
from api.repositories.bet_repository import BetRepository
from api.schemas.bet_schemas import BetResolveRequest, BetDisputeRequest


class TestBetResolutionErrorHandling:
    """Test error handling in bet resolution"""
    
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
    def test_database_connection_error(self, mock_get_db, mock_get_current_user, 
                                     client, mock_user):
        """Test handling of database connection errors"""
        mock_get_current_user.return_value = mock_user
        
        # Mock database session that raises connection error
        mock_db = Mock(spec=Session)
        mock_db.query.side_effect = SQLAlchemyError("Database connection failed")
        mock_get_db.return_value = mock_db
        
        request_data = {"result": "win"}
        response = client.post("/api/v1/bets/1/resolve", json=request_data)
        
        assert response.status_code == 500
        assert "Failed to resolve bet" in response.json()["detail"]

    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_database_integrity_error(self, mock_get_db, mock_get_current_user, 
                                    client, mock_user):
        """Test handling of database integrity errors"""
        mock_get_current_user.return_value = mock_user
        mock_get_db.return_value = Mock(spec=Session)
        
        with patch('api.endpoints.bets.BetService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            mock_service_instance.resolve_bet.side_effect = IntegrityError(
                statement="INSERT INTO bets",
                params={},
                orig=Exception("UNIQUE constraint failed")
            )
            
            request_data = {"result": "win"}
            response = client.post("/api/v1/bets/1/resolve", json=request_data)
            
            assert response.status_code == 500
            assert "Failed to resolve bet" in response.json()["detail"]

    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_websocket_error_during_resolution(self, mock_get_db, mock_get_current_user, 
                                             client, mock_user, mock_bet):
        """Test that WebSocket errors don't break resolution"""
        mock_get_current_user.return_value = mock_user
        mock_get_db.return_value = Mock(spec=Session)
        
        with patch('api.endpoints.bets.BetService') as mock_service, \
             patch('api.endpoints.bets.send_bet_status_update') as mock_ws:
            
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            
            # Mock successful resolution
            resolved_bet = mock_bet
            resolved_bet.status = "resolved"
            resolved_bet.result = "win"
            resolved_bet.user = Mock()
            resolved_bet.user.email = "test@example.com"
            mock_service_instance.resolve_bet.return_value = resolved_bet
            
            # Mock WebSocket error
            mock_ws.side_effect = Exception("WebSocket connection failed")
            
            request_data = {"result": "win"}
            response = client.post("/api/v1/bets/1/resolve", json=request_data)
            
            # Resolution should still succeed despite WebSocket error
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "resolved"

    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_email_error_during_resolution(self, mock_get_db, mock_get_current_user, 
                                         client, mock_user, mock_bet):
        """Test that email errors don't break resolution"""
        mock_get_current_user.return_value = mock_user
        mock_get_db.return_value = Mock(spec=Session)
        
        with patch('api.endpoints.bets.BetService') as mock_service, \
             patch('api.endpoints.bets.send_bet_resolution_notification') as mock_email:
            
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            
            # Mock successful resolution
            resolved_bet = mock_bet
            resolved_bet.status = "resolved"
            resolved_bet.result = "win"
            resolved_bet.user = Mock()
            resolved_bet.user.email = "test@example.com"
            mock_service_instance.resolve_bet.return_value = resolved_bet
            
            # Mock email error
            mock_email.side_effect = Exception("Email service unavailable")
            
            request_data = {"result": "win"}
            response = client.post("/api/v1/bets/1/resolve", json=request_data)
            
            # Resolution should still succeed despite email error
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "resolved"

    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_validation_error_handling(self, mock_get_db, mock_get_current_user, client):
        """Test validation error handling"""
        mock_get_current_user.return_value = {"external_id": "test_user_123"}
        mock_get_db.return_value = Mock(spec=Session)
        
        # Test missing required fields
        response = client.post("/api/v1/bets/1/resolve", json={})
        assert response.status_code == 422
        
        # Test invalid result value
        response = client.post("/api/v1/bets/1/resolve", json={"result": "invalid"})
        assert response.status_code == 422
        
        # Test invalid dispute reason (too short)
        response = client.post("/api/v1/bets/1/dispute", json={"dispute_reason": "Bad"})
        assert response.status_code == 422

    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_authorization_error_handling(self, mock_get_db, mock_get_current_user, 
                                        client, mock_user):
        """Test authorization error handling"""
        mock_get_current_user.return_value = mock_user
        mock_get_db.return_value = Mock(spec=Session)
        
        with patch('api.endpoints.bets.BetService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            mock_service_instance.resolve_bet.side_effect = ValueError("User not authorized to resolve this bet")
            
            request_data = {"result": "win"}
            response = client.post("/api/v1/bets/1/resolve", json=request_data)
            
            assert response.status_code == 400
            assert "not authorized" in response.json()["detail"]

    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_bet_not_found_error(self, mock_get_db, mock_get_current_user, 
                               client, mock_user):
        """Test bet not found error handling"""
        mock_get_current_user.return_value = mock_user
        mock_get_db.return_value = Mock(spec=Session)
        
        with patch('api.endpoints.bets.BetService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            mock_service_instance.resolve_bet.side_effect = ValueError("Bet not found")
            
            request_data = {"result": "win"}
            response = client.post("/api/v1/bets/999/resolve", json=request_data)
            
            assert response.status_code == 400
            assert "Bet not found" in response.json()["detail"]

    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_user_not_found_error(self, mock_get_db, mock_get_current_user, 
                                client, mock_user):
        """Test user not found error handling"""
        mock_get_current_user.return_value = mock_user
        mock_get_db.return_value = Mock(spec=Session)
        
        with patch('api.endpoints.bets.BetService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            mock_service_instance.resolve_bet.side_effect = ValueError("User not found")
            
            request_data = {"result": "win"}
            response = client.post("/api/v1/bets/1/resolve", json=request_data)
            
            assert response.status_code == 400
            assert "User not found" in response.json()["detail"]

    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_concurrent_modification_error(self, mock_get_db, mock_get_current_user, 
                                         client, mock_user):
        """Test handling of concurrent modification errors"""
        mock_get_current_user.return_value = mock_user
        mock_get_db.return_value = Mock(spec=Session)
        
        with patch('api.endpoints.bets.BetService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            mock_service_instance.resolve_bet.side_effect = ValueError("Bet has been modified by another user")
            
            request_data = {"result": "win"}
            response = client.post("/api/v1/bets/1/resolve", json=request_data)
            
            assert response.status_code == 400
            assert "modified by another user" in response.json()["detail"]

    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_already_resolved_error(self, mock_get_db, mock_get_current_user, 
                                  client, mock_user):
        """Test handling of already resolved bet error"""
        mock_get_current_user.return_value = mock_user
        mock_get_db.return_value = Mock(spec=Session)
        
        with patch('api.endpoints.bets.BetService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            mock_service_instance.resolve_bet.side_effect = ValueError("Bet has already been resolved")
            
            request_data = {"result": "win"}
            response = client.post("/api/v1/bets/1/resolve", json=request_data)
            
            assert response.status_code == 400
            assert "already been resolved" in response.json()["detail"]

    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_already_disputed_error(self, mock_get_db, mock_get_current_user, 
                                  client, mock_user):
        """Test handling of already disputed bet error"""
        mock_get_current_user.return_value = mock_user
        mock_get_db.return_value = Mock(spec=Session)
        
        with patch('api.endpoints.bets.BetService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            mock_service_instance.dispute_bet_resolution.side_effect = ValueError("Bet is already disputed")
            
            request_data = {"dispute_reason": "Score was incorrect according to official stats"}
            response = client.post("/api/v1/bets/1/dispute", json=request_data)
            
            assert response.status_code == 400
            assert "already disputed" in response.json()["detail"]

    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_invalid_result_transition_error(self, mock_get_db, mock_get_current_user, 
                                           client, mock_user):
        """Test handling of invalid result transition errors"""
        mock_get_current_user.return_value = mock_user
        mock_get_db.return_value = Mock(spec=Session)
        
        with patch('api.endpoints.bets.BetService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            mock_service_instance.resolve_bet.side_effect = ValueError("Invalid status transition from resolved to pending")
            
            request_data = {"result": "win"}
            response = client.post("/api/v1/bets/1/resolve", json=request_data)
            
            assert response.status_code == 400
            assert "Invalid status transition" in response.json()["detail"]

    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_network_timeout_error(self, mock_get_db, mock_get_current_user, 
                                 client, mock_user):
        """Test handling of network timeout errors"""
        mock_get_current_user.return_value = mock_user
        mock_get_db.return_value = Mock(spec=Session)
        
        with patch('api.endpoints.bets.BetService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            mock_service_instance.resolve_bet.side_effect = TimeoutError("Request timed out")
            
            request_data = {"result": "win"}
            response = client.post("/api/v1/bets/1/resolve", json=request_data)
            
            assert response.status_code == 500
            assert "Failed to resolve bet" in response.json()["detail"]

    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_service_unavailable_error(self, mock_get_db, mock_get_current_user, 
                                     client, mock_user):
        """Test handling of service unavailable errors"""
        mock_get_current_user.return_value = mock_user
        mock_get_db.return_value = Mock(spec=Session)
        
        with patch('api.endpoints.bets.BetService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            mock_service_instance.resolve_bet.side_effect = ConnectionError("Service unavailable")
            
            request_data = {"result": "win"}
            response = client.post("/api/v1/bets/1/resolve", json=request_data)
            
            assert response.status_code == 500
            assert "Failed to resolve bet" in response.json()["detail"]

    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_memory_error_handling(self, mock_get_db, mock_get_current_user, 
                                 client, mock_user):
        """Test handling of memory errors"""
        mock_get_current_user.return_value = mock_user
        mock_get_db.return_value = Mock(spec=Session)
        
        with patch('api.endpoints.bets.BetService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            mock_service_instance.resolve_bet.side_effect = MemoryError("Out of memory")
            
            request_data = {"result": "win"}
            response = client.post("/api/v1/bets/1/resolve", json=request_data)
            
            assert response.status_code == 500
            assert "Failed to resolve bet" in response.json()["detail"]

    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_unicode_error_handling(self, mock_get_db, mock_get_current_user, 
                                  client, mock_user):
        """Test handling of Unicode errors in resolution notes"""
        mock_get_current_user.return_value = mock_user
        mock_get_db.return_value = Mock(spec=Session)
        
        with patch('api.endpoints.bets.BetService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            mock_service_instance.resolve_bet.side_effect = UnicodeError("Unicode decode error")
            
            request_data = {
                "result": "win",
                "resolution_notes": "Game completed with special characters: émojis 🏈"
            }
            response = client.post("/api/v1/bets/1/resolve", json=request_data)
            
            assert response.status_code == 500
            assert "Failed to resolve bet" in response.json()["detail"]

    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_rate_limit_error_handling(self, mock_get_db, mock_get_current_user, 
                                     client, mock_user):
        """Test handling of rate limit errors"""
        mock_get_current_user.return_value = mock_user
        mock_get_db.return_value = Mock(spec=Session)
        
        with patch('api.endpoints.bets.BetService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            mock_service_instance.resolve_bet.side_effect = ValueError("Rate limit exceeded")
            
            request_data = {"result": "win"}
            response = client.post("/api/v1/bets/1/resolve", json=request_data)
            
            assert response.status_code == 400
            assert "Rate limit exceeded" in response.json()["detail"]

    def test_service_layer_error_propagation(self):
        """Test error propagation from service layer"""
        mock_db = Mock(spec=Session)
        mock_repository = Mock(spec=BetRepository)
        
        bet_service = BetService(mock_db)
        bet_service.bet_repository = mock_repository
        
        # Test repository error propagation
        mock_repository.get_bet_with_user.side_effect = SQLAlchemyError("Database error")
        
        request = BetResolveRequest(result="win")
        
        with pytest.raises(SQLAlchemyError):
            bet_service.resolve_bet(1, request, 1)

    def test_repository_error_handling(self):
        """Test repository error handling"""
        mock_db = Mock(spec=Session)
        mock_repository = Mock(spec=BetRepository)
        
        bet_service = BetService(mock_db)
        bet_service.bet_repository = mock_repository
        
        # Test repository returning None
        mock_repository.get_bet_with_user.return_value = None
        
        request = BetResolveRequest(result="win")
        
        with pytest.raises(ValueError, match="Bet not found"):
            bet_service.resolve_bet(999, request, 1)

    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_partial_failure_recovery(self, mock_get_db, mock_get_current_user, 
                                    client, mock_user, mock_bet):
        """Test recovery from partial failures"""
        mock_get_current_user.return_value = mock_user
        mock_get_db.return_value = Mock(spec=Session)
        
        with patch('api.endpoints.bets.BetService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            
            # Mock successful resolution
            resolved_bet = mock_bet
            resolved_bet.status = "resolved"
            resolved_bet.result = "win"
            resolved_bet.user = Mock()
            resolved_bet.user.email = "test@example.com"
            mock_service_instance.resolve_bet.return_value = resolved_bet
            
            # Mock partial failures (WebSocket and email fail, but resolution succeeds)
            with patch('api.endpoints.bets.send_bet_status_update') as mock_ws, \
                 patch('api.endpoints.bets.send_bet_resolution_notification') as mock_email:
                
                mock_ws.side_effect = Exception("WebSocket failed")
                mock_email.side_effect = Exception("Email failed")
                
                request_data = {"result": "win"}
                response = client.post("/api/v1/bets/1/resolve", json=request_data)
                
                # Resolution should still succeed despite partial failures
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "resolved"

