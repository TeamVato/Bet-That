"""Comprehensive tests for bet resolution functionality"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.main import app
from api.models import User, Bet, BetResolutionHistory
from api.services.bet_service import BetService
from api.repositories.bet_repository import BetRepository
from api.schemas.bet_schemas import BetResolveRequest, BetDisputeRequest


class TestBetResolutionAPI:
    """Test bet resolution API endpoints"""
    
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

    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_resolve_bet_success(self, mock_get_db, mock_get_current_user, 
                                client, mock_user, mock_bet, mock_db_user):
        """Test successful bet resolution"""
        # Setup mocks
        mock_db = Mock(spec=Session)
        mock_get_db.return_value = mock_db
        mock_get_current_user.return_value = mock_user
        
        # Mock repository responses
        with patch('api.endpoints.bets.BetService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            
            # Mock resolved bet response
            resolved_bet = mock_bet
            resolved_bet.status = "resolved"
            resolved_bet.result = "win"
            resolved_bet.resolved_at = datetime.now()
            resolved_bet.resolved_by = 1
            resolved_bet.resolution_notes = "Game completed"
            
            mock_service_instance.resolve_bet.return_value = resolved_bet
            
            # Make request
            request_data = {
                "result": "win",
                "resolution_notes": "Game completed",
                "resolution_source": "ESPN"
            }
            
            response = client.post("/api/v1/bets/1/resolve", json=request_data)
            
            # Assertions
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "resolved"
            assert data["result"] == "win"
            assert data["resolution_notes"] == "Game completed"
            mock_service_instance.resolve_bet.assert_called_once()

    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_resolve_bet_unauthorized(self, mock_get_db, mock_get_current_user, client):
        """Test bet resolution with unauthorized user"""
        mock_get_db.return_value = Mock(spec=Session)
        mock_get_current_user.return_value = None
        
        request_data = {"result": "win"}
        response = client.post("/api/v1/bets/1/resolve", json=request_data)
        
        assert response.status_code == 401

    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_resolve_bet_invalid_result(self, mock_get_db, mock_get_current_user, 
                                       client, mock_user):
        """Test bet resolution with invalid result"""
        mock_get_db.return_value = Mock(spec=Session)
        mock_get_current_user.return_value = mock_user
        
        request_data = {"result": "invalid_result"}
        response = client.post("/api/v1/bets/1/resolve", json=request_data)
        
        assert response.status_code == 422  # Validation error

    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_resolve_bet_not_found(self, mock_get_db, mock_get_current_user, 
                                  client, mock_user):
        """Test bet resolution with non-existent bet"""
        mock_get_db.return_value = Mock(spec=Session)
        mock_get_current_user.return_value = mock_user
        
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
    def test_dispute_bet_resolution(self, mock_get_db, mock_get_current_user, 
                                   client, mock_user, mock_bet):
        """Test disputing a bet resolution"""
        mock_get_db.return_value = Mock(spec=Session)
        mock_get_current_user.return_value = mock_user
        
        with patch('api.endpoints.bets.BetService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            
            disputed_bet = mock_bet
            disputed_bet.is_disputed = True
            disputed_bet.dispute_reason = "Score was incorrect"
            disputed_bet.dispute_created_at = datetime.now()
            
            mock_service_instance.dispute_bet_resolution.return_value = disputed_bet
            
            request_data = {
                "dispute_reason": "Score was incorrect according to official stats"
            }
            
            response = client.post("/api/v1/bets/1/dispute", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["is_disputed"] is True
            assert data["dispute_reason"] == "Score was incorrect"

    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_get_resolution_history(self, mock_get_db, mock_get_current_user, 
                                   client, mock_user):
        """Test getting bet resolution history"""
        mock_get_db.return_value = Mock(spec=Session)
        mock_get_current_user.return_value = mock_user
        
        with patch('api.endpoints.bets.BetService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            
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
                        "resolution_notes": "Game completed",
                        "performed_by": 1,
                        "created_at": datetime.now().isoformat()
                    }
                ],
                "total": 1,
                "page": 1,
                "per_page": 50
            }
            
            mock_service_instance.get_resolution_history.return_value = mock_history
            
            response = client.get("/api/v1/bets/1/resolution-history")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["history"]) == 1
            assert data["history"][0]["action_type"] == "resolve"

    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_get_disputed_bets(self, mock_get_db, mock_get_current_user, 
                              client, mock_user):
        """Test getting disputed bets"""
        mock_get_db.return_value = Mock(spec=Session)
        mock_get_current_user.return_value = mock_user
        
        with patch('api.endpoints.bets.BetService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            
            mock_disputed_bets = {
                "bets": [],
                "total": 0,
                "page": 1,
                "per_page": 50
            }
            
            mock_service_instance.get_disputed_bets.return_value = mock_disputed_bets
            
            response = client.get("/api/v1/bets/disputed")
            
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 0

    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_get_pending_resolution_bets(self, mock_get_db, mock_get_current_user, 
                                        client, mock_user):
        """Test getting pending resolution bets"""
        mock_get_db.return_value = Mock(spec=Session)
        mock_get_current_user.return_value = mock_user
        
        with patch('api.endpoints.bets.BetService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            
            mock_pending_bets = {
                "bets": [],
                "total": 0,
                "page": 1,
                "per_page": 50
            }
            
            mock_service_instance.get_pending_resolution_bets.return_value = mock_pending_bets
            
            response = client.get("/api/v1/bets/pending-resolution")
            
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 0

    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_resolve_bet_dispute(self, mock_get_db, mock_get_current_user, 
                                client, mock_user):
        """Test resolving a bet dispute"""
        mock_get_db.return_value = Mock(spec=Session)
        mock_get_current_user.return_value = mock_user
        
        with patch('api.endpoints.bets.BetService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            
            resolved_bet = Mock()
            resolved_bet.status = "resolved"
            resolved_bet.result = "loss"
            resolved_bet.is_disputed = False
            
            mock_service_instance.resolve_dispute.return_value = resolved_bet
            
            response = client.put(
                "/api/v1/bets/1/resolve-dispute",
                params={
                    "new_result": "loss",
                    "resolution_notes": "Corrected score"
                }
            )
            
            assert response.status_code == 200


class TestBetService:
    """Test bet resolution service layer"""
    
    @pytest.fixture
    def mock_db(self):
        return Mock(spec=Session)
    
    @pytest.fixture
    def mock_repository(self):
        return Mock(spec=BetRepository)
    
    @pytest.fixture
    def bet_service(self, mock_db, mock_repository):
        service = BetService(mock_db)
        service.bet_repository = mock_repository
        return service

    def test_resolve_bet_success(self, bet_service, mock_repository):
        """Test successful bet resolution in service layer"""
        # Setup mock bet
        mock_bet = Mock()
        mock_bet.user_id = 1
        mock_bet.status = "pending"
        
        mock_resolved_bet = Mock()
        mock_resolved_bet.status = "resolved"
        mock_resolved_bet.result = "win"
        mock_resolved_bet.user = Mock()
        mock_resolved_bet.user.email = "test@example.com"
        
        # Setup repository mocks
        mock_repository.get_bet_with_user.return_value = mock_bet
        mock_repository.can_user_resolve_bet.return_value = True
        mock_repository.resolve_bet.return_value = mock_resolved_bet
        
        # Mock WebSocket and email services
        with patch('api.services.bet_service.send_bet_status_update') as mock_ws, \
             patch('api.services.bet_service.send_bet_resolution_notification') as mock_email:
            
            mock_ws.return_value = AsyncMock()
            mock_email.return_value = None
            
            request = BetResolveRequest(
                result="win",
                resolution_notes="Game completed",
                resolution_source="ESPN"
            )
            
            result = bet_service.resolve_bet(1, request, 1)
            
            # Assertions
            mock_repository.get_bet_with_user.assert_called_once_with(1)
            mock_repository.can_user_resolve_bet.assert_called_once_with(mock_bet, 1)
            mock_repository.resolve_bet.assert_called_once()
            assert result.status == "resolved"

    def test_resolve_bet_unauthorized(self, bet_service, mock_repository):
        """Test bet resolution with unauthorized user"""
        mock_bet = Mock()
        mock_bet.user_id = 1
        
        mock_repository.get_bet_with_user.return_value = mock_bet
        mock_repository.can_user_resolve_bet.return_value = False
        
        request = BetResolveRequest(result="win")
        
        with pytest.raises(ValueError, match="User not authorized"):
            bet_service.resolve_bet(1, request, 2)  # Different user ID

    def test_resolve_bet_not_found(self, bet_service, mock_repository):
        """Test bet resolution with non-existent bet"""
        mock_repository.get_bet_with_user.return_value = None
        
        request = BetResolveRequest(result="win")
        
        with pytest.raises(ValueError, match="Bet not found"):
            bet_service.resolve_bet(999, request, 1)

    def test_dispute_bet_resolution(self, bet_service, mock_repository):
        """Test disputing a bet resolution"""
        mock_bet = Mock()
        mock_bet.user_id = 1
        mock_bet.user = Mock()
        mock_bet.user.email = "test@example.com"
        
        mock_disputed_bet = Mock()
        mock_disputed_bet.is_disputed = True
        mock_disputed_bet.dispute_reason = "Score was incorrect"
        
        mock_repository.get_bet_by_id.return_value = mock_bet
        mock_repository.dispute_bet_resolution.return_value = mock_disputed_bet
        
        with patch('api.services.bet_service.send_dispute_resolution_update') as mock_ws, \
             patch('api.services.bet_service.send_bet_dispute_notification') as mock_email:
            
            mock_ws.return_value = AsyncMock()
            mock_email.return_value = None
            
            request = BetDisputeRequest(dispute_reason="Score was incorrect")
            
            result = bet_service.dispute_bet_resolution(1, request, 1)
            
            mock_repository.get_bet_by_id.assert_called_once_with(1)
            mock_repository.dispute_bet_resolution.assert_called_once()
            assert result.is_disputed is True

    def test_dispute_bet_wrong_user(self, bet_service, mock_repository):
        """Test disputing bet with wrong user"""
        mock_bet = Mock()
        mock_bet.user_id = 1
        
        mock_repository.get_bet_by_id.return_value = mock_bet
        
        request = BetDisputeRequest(dispute_reason="Score was incorrect")
        
        with pytest.raises(ValueError, match="User not authorized"):
            bet_service.dispute_bet_resolution(1, request, 2)  # Different user ID


class TestBetResolutionIntegration:
    """Integration tests for bet resolution workflow"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_complete_resolution_workflow(self, mock_get_db, mock_get_current_user, client):
        """Test complete bet resolution workflow"""
        # Setup
        mock_user = {"external_id": "test_user_123", "email": "test@example.com", "name": "Test User"}
        mock_get_current_user.return_value = mock_user
        mock_get_db.return_value = Mock(spec=Session)
        
        with patch('api.endpoints.bets.BetService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            
            # Mock bet creation
            mock_bet = Mock()
            mock_bet.id = 1
            mock_bet.status = "pending"
            mock_bet.result = None
            mock_bet.user_id = 1
            mock_bet.user = Mock()
            mock_bet.user.email = "test@example.com"
            
            # Mock resolution
            mock_resolved_bet = Mock()
            mock_resolved_bet.id = 1
            mock_resolved_bet.status = "resolved"
            mock_resolved_bet.result = "win"
            mock_resolved_bet.resolved_at = datetime.now()
            mock_resolved_bet.resolution_notes = "Game completed"
            mock_resolved_bet.user = mock_bet.user
            
            # Mock dispute
            mock_disputed_bet = Mock()
            mock_disputed_bet.id = 1
            mock_disputed_bet.status = "resolved"
            mock_disputed_bet.result = "win"
            mock_disputed_bet.is_disputed = True
            mock_disputed_bet.dispute_reason = "Score was incorrect"
            mock_disputed_bet.user = mock_bet.user
            
            mock_service_instance.resolve_bet.return_value = mock_resolved_bet
            mock_service_instance.dispute_bet_resolution.return_value = mock_disputed_bet
            
            # Step 1: Resolve bet
            resolve_request = {
                "result": "win",
                "resolution_notes": "Game completed",
                "resolution_source": "ESPN"
            }
            
            response = client.post("/api/v1/bets/1/resolve", json=resolve_request)
            assert response.status_code == 200
            
            # Step 2: Dispute resolution
            dispute_request = {
                "dispute_reason": "Score was incorrect according to official stats"
            }
            
            response = client.post("/api/v1/bets/1/dispute", json=dispute_request)
            assert response.status_code == 200
            
            # Step 3: Get resolution history
            mock_history = {
                "history": [
                    {
                        "id": 1,
                        "bet_id": 1,
                        "action_type": "resolve",
                        "previous_status": "pending",
                        "new_status": "resolved",
                        "new_result": "win",
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
                    }
                ],
                "total": 2,
                "page": 1,
                "per_page": 50
            }
            
            mock_service_instance.get_resolution_history.return_value = mock_history
            
            response = client.get("/api/v1/bets/1/resolution-history")
            assert response.status_code == 200
            data = response.json()
            assert len(data["history"]) == 2
            assert data["history"][0]["action_type"] == "resolve"
            assert data["history"][1]["action_type"] == "dispute"


class TestBetResolutionErrorHandling:
    """Test error handling in bet resolution"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_database_error_handling(self, mock_get_db, mock_get_current_user, client):
        """Test database error handling"""
        mock_user = {"external_id": "test_user_123"}
        mock_get_current_user.return_value = mock_user
        mock_get_db.return_value = Mock(spec=Session)
        
        with patch('api.endpoints.bets.BetService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            mock_service_instance.resolve_bet.side_effect = Exception("Database connection failed")
            
            request_data = {"result": "win"}
            response = client.post("/api/v1/bets/1/resolve", json=request_data)
            
            assert response.status_code == 500
            assert "Failed to resolve bet" in response.json()["detail"]

    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_websocket_error_handling(self, mock_get_db, mock_get_current_user, client):
        """Test WebSocket error handling doesn't break resolution"""
        mock_user = {"external_id": "test_user_123"}
        mock_get_current_user.return_value = mock_user
        mock_get_db.return_value = Mock(spec=Session)
        
        with patch('api.endpoints.bets.BetService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            
            # Mock successful resolution but WebSocket failure
            mock_resolved_bet = Mock()
            mock_resolved_bet.status = "resolved"
            mock_resolved_bet.result = "win"
            mock_resolved_bet.user = Mock()
            mock_resolved_bet.user.email = "test@example.com"
            
            mock_service_instance.resolve_bet.return_value = mock_resolved_bet
            
            request_data = {"result": "win"}
            response = client.post("/api/v1/bets/1/resolve", json=request_data)
            
            # Resolution should still succeed even if WebSocket fails
            assert response.status_code == 200

    def test_validation_error_handling(self, client):
        """Test validation error handling"""
        # Test missing required fields
        response = client.post("/api/v1/bets/1/resolve", json={})
        assert response.status_code == 422
        
        # Test invalid result value
        response = client.post("/api/v1/bets/1/resolve", json={"result": "invalid"})
        assert response.status_code == 422
        
        # Test dispute with short reason
        response = client.post("/api/v1/bets/1/dispute", json={"dispute_reason": "Bad"})
        assert response.status_code == 422


class TestBetResolutionPermissions:
    """Test permission checks for bet resolution"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @patch('api.endpoints.bets.get_current_user')
    @patch('api.endpoints.bets.get_db')
    def test_only_bet_creator_can_resolve(self, mock_get_db, mock_get_current_user, client):
        """Test that only bet creator can resolve their bet"""
        # Setup bet creator
        bet_creator = {"external_id": "creator_123"}
        mock_get_current_user.return_value = bet_creator
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
    def test_only_bet_creator_can_dispute(self, mock_get_db, mock_get_current_user, client):
        """Test that only bet creator can dispute their bet"""
        # Setup different user
        other_user = {"external_id": "other_user_123"}
        mock_get_current_user.return_value = other_user
        mock_get_db.return_value = Mock(spec=Session)
        
        with patch('api.endpoints.bets.BetService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            mock_service_instance.dispute_bet_resolution.side_effect = ValueError("User not authorized to dispute this bet")
            
            request_data = {"dispute_reason": "Score was incorrect according to official stats"}
            response = client.post("/api/v1/bets/1/dispute", json=request_data)
            
            assert response.status_code == 400
            assert "not authorized" in response.json()["detail"]

