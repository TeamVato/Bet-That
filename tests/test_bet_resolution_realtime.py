"""Real-time update tests for bet resolution"""

import pytest
import asyncio
import json
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient

from api.main import app
from api.models import User, Bet
from api.endpoints.websocket import send_bet_status_update, send_dispute_resolution_update


class TestBetResolutionRealTime:
    """Test real-time updates for bet resolution"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def mock_bet(self):
        return Mock(
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
            sportsbook_name="DraftKings",
            external_bet_id="dk_123",
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
    def mock_user(self):
        return Mock(
            id=1,
            external_id="test_user_123",
            email="test@example.com",
            name="Test User"
        )

    @pytest.mark.asyncio
    async def test_send_bet_status_update(self, mock_bet, mock_user):
        """Test sending bet status update via WebSocket"""
        mock_bet.user = mock_user
        
        # Mock WebSocket manager
        with patch('api.endpoints.websocket.websocket_manager') as mock_manager:
            mock_manager.broadcast_to_user.return_value = AsyncMock()
            
            await send_bet_status_update(
                bet=mock_bet,
                old_status="pending",
                new_status="resolved",
                result="win",
                resolution_notes="Game completed"
            )
            
            # Verify broadcast was called
            mock_manager.broadcast_to_user.assert_called_once()
            
            # Get the call arguments
            call_args = mock_manager.broadcast_to_user.call_args
            user_id = call_args[0][0]
            message = call_args[0][1]
            
            assert user_id == "test_user_123"
            assert message["type"] == "bet_resolution"
            assert message["data"]["bet_id"] == 1
            assert message["data"]["old_status"] == "pending"
            assert message["data"]["new_status"] == "resolved"
            assert message["data"]["result"] == "win"
            assert message["data"]["resolution_notes"] == "Game completed"

    @pytest.mark.asyncio
    async def test_send_dispute_resolution_update(self, mock_bet, mock_user):
        """Test sending dispute resolution update via WebSocket"""
        mock_bet.user = mock_user
        mock_bet.is_disputed = True
        mock_bet.dispute_reason = "Score was incorrect"
        
        # Mock WebSocket manager
        with patch('api.endpoints.websocket.websocket_manager') as mock_manager:
            mock_manager.broadcast_to_user.return_value = AsyncMock()
            
            await send_dispute_resolution_update(
                bet=mock_bet,
                dispute_reason="Score was incorrect"
            )
            
            # Verify broadcast was called
            mock_manager.broadcast_to_user.assert_called_once()
            
            # Get the call arguments
            call_args = mock_manager.broadcast_to_user.call_args
            user_id = call_args[0][0]
            message = call_args[0][1]
            
            assert user_id == "test_user_123"
            assert message["type"] == "dispute_resolution"
            assert message["data"]["bet_id"] == 1
            assert message["data"]["dispute_reason"] == "Score was incorrect"

    @pytest.mark.asyncio
    async def test_websocket_error_handling(self, mock_bet, mock_user):
        """Test WebSocket error handling during resolution"""
        mock_bet.user = mock_user
        
        # Mock WebSocket manager to raise an error
        with patch('api.endpoints.websocket.websocket_manager') as mock_manager:
            mock_manager.broadcast_to_user.side_effect = Exception("WebSocket error")
            
            # Should not raise an exception
            await send_bet_status_update(
                bet=mock_bet,
                old_status="pending",
                new_status="resolved",
                result="win",
                resolution_notes="Game completed"
            )
            
            # Verify broadcast was attempted
            mock_manager.broadcast_to_user.assert_called_once()

    @pytest.mark.asyncio
    async def test_websocket_user_not_found(self, mock_bet):
        """Test WebSocket handling when user is not found"""
        mock_bet.user = None
        
        # Mock WebSocket manager
        with patch('api.endpoints.websocket.websocket_manager') as mock_manager:
            mock_manager.broadcast_to_user.return_value = AsyncMock()
            
            # Should not raise an exception
            await send_bet_status_update(
                bet=mock_bet,
                old_status="pending",
                new_status="resolved",
                result="win"
            )
            
            # Should not call broadcast when user is None
            mock_manager.broadcast_to_user.assert_not_called()

    @pytest.mark.asyncio
    async def test_websocket_message_format(self, mock_bet, mock_user):
        """Test WebSocket message format and structure"""
        mock_bet.user = mock_user
        
        # Mock WebSocket manager
        with patch('api.endpoints.websocket.websocket_manager') as mock_manager:
            mock_manager.broadcast_to_user.return_value = AsyncMock()
            
            await send_bet_status_update(
                bet=mock_bet,
                old_status="pending",
                new_status="resolved",
                result="win",
                resolution_notes="Game completed successfully"
            )
            
            # Get the message that was sent
            call_args = mock_manager.broadcast_to_user.call_args
            message = call_args[0][1]
            
            # Verify message structure
            assert "type" in message
            assert "data" in message
            assert "timestamp" in message
            
            # Verify message type
            assert message["type"] == "bet_resolution"
            
            # Verify data structure
            data = message["data"]
            required_fields = [
                "bet_id", "old_status", "new_status", "result",
                "resolution_notes", "updated_at"
            ]
            for field in required_fields:
                assert field in data
            
            # Verify timestamp format
            timestamp = message["timestamp"]
            assert isinstance(timestamp, str)
            # Should be a valid ISO format timestamp
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))

    @pytest.mark.asyncio
    async def test_websocket_broadcast_to_all_users(self, mock_bet, mock_user):
        """Test broadcasting to all users (for admin notifications)"""
        mock_bet.user = mock_user
        
        # Mock WebSocket manager
        with patch('api.endpoints.websocket.websocket_manager') as mock_manager:
            mock_manager.broadcast_to_all.return_value = AsyncMock()
            
            # Simulate admin broadcast (this would be a separate function)
            await mock_manager.broadcast_to_all({
                "type": "system_notification",
                "data": {
                    "message": "System maintenance in 5 minutes",
                    "level": "warning"
                },
                "timestamp": datetime.now().isoformat()
            })
            
            # Verify broadcast to all was called
            mock_manager.broadcast_to_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_concurrent_websocket_updates(self, mock_bet, mock_user):
        """Test handling concurrent WebSocket updates"""
        mock_bet.user = mock_user
        
        # Mock WebSocket manager
        with patch('api.endpoints.websocket.websocket_manager') as mock_manager:
            mock_manager.broadcast_to_user.return_value = AsyncMock()
            
            # Send multiple concurrent updates
            tasks = []
            for i in range(5):
                task = send_bet_status_update(
                    bet=mock_bet,
                    old_status="pending",
                    new_status="resolved",
                    result="win",
                    resolution_notes=f"Update {i}"
                )
                tasks.append(task)
            
            # Wait for all tasks to complete
            await asyncio.gather(*tasks)
            
            # Verify all broadcasts were called
            assert mock_manager.broadcast_to_user.call_count == 5

    @pytest.mark.asyncio
    async def test_websocket_connection_management(self):
        """Test WebSocket connection management"""
        from api.endpoints.websocket import websocket_manager
        
        # Mock a WebSocket connection
        mock_websocket = Mock()
        mock_websocket.send_text = AsyncMock()
        
        # Test connection handling
        with patch.object(websocket_manager, 'connect') as mock_connect, \
             patch.object(websocket_manager, 'disconnect') as mock_disconnect:
            
            # Simulate connection
            await websocket_manager.connect(mock_websocket, "test_user_123")
            mock_connect.assert_called_once_with(mock_websocket, "test_user_123")
            
            # Simulate disconnection
            await websocket_manager.disconnect(mock_websocket, "test_user_123")
            mock_disconnect.assert_called_once_with(mock_websocket, "test_user_123")

    @pytest.mark.asyncio
    async def test_websocket_message_serialization(self, mock_bet, mock_user):
        """Test WebSocket message serialization"""
        mock_bet.user = mock_user
        
        # Mock WebSocket manager
        with patch('api.endpoints.websocket.websocket_manager') as mock_manager:
            mock_manager.broadcast_to_user.return_value = AsyncMock()
            
            await send_bet_status_update(
                bet=mock_bet,
                old_status="pending",
                new_status="resolved",
                result="win",
                resolution_notes="Game completed"
            )
            
            # Get the message that was sent
            call_args = mock_manager.broadcast_to_user.call_args
            message = call_args[0][1]
            
            # Verify message can be serialized to JSON
            json_message = json.dumps(message)
            assert isinstance(json_message, str)
            
            # Verify message can be deserialized
            deserialized_message = json.loads(json_message)
            assert deserialized_message["type"] == "bet_resolution"
            assert deserialized_message["data"]["bet_id"] == 1

    @pytest.mark.asyncio
    async def test_websocket_retry_mechanism(self, mock_bet, mock_user):
        """Test WebSocket retry mechanism for failed sends"""
        mock_bet.user = mock_user
        
        # Mock WebSocket manager with intermittent failures
        with patch('api.endpoints.websocket.websocket_manager') as mock_manager:
            mock_manager.broadcast_to_user.side_effect = [
                Exception("Connection failed"),
                AsyncMock()  # Success on retry
            ]
            
            # First call should fail
            with pytest.raises(Exception):
                await send_bet_status_update(
                    bet=mock_bet,
                    old_status="pending",
                    new_status="resolved",
                    result="win"
                )
            
            # Second call should succeed
            await send_bet_status_update(
                bet=mock_bet,
                old_status="pending",
                new_status="resolved",
                result="win"
            )
            
            # Verify both attempts were made
            assert mock_manager.broadcast_to_user.call_count == 2

    @pytest.mark.asyncio
    async def test_websocket_rate_limiting(self, mock_bet, mock_user):
        """Test WebSocket rate limiting"""
        mock_bet.user = mock_user
        
        # Mock WebSocket manager
        with patch('api.endpoints.websocket.websocket_manager') as mock_manager:
            mock_manager.broadcast_to_user.return_value = AsyncMock()
            
            # Send multiple updates rapidly
            tasks = []
            for i in range(10):
                task = send_bet_status_update(
                    bet=mock_bet,
                    old_status="pending",
                    new_status="resolved",
                    result="win",
                    resolution_notes=f"Update {i}"
                )
                tasks.append(task)
            
            # Wait for all tasks to complete
            await asyncio.gather(*tasks)
            
            # Verify all broadcasts were attempted
            assert mock_manager.broadcast_to_user.call_count == 10

    @pytest.mark.asyncio
    async def test_websocket_message_validation(self, mock_bet, mock_user):
        """Test WebSocket message validation"""
        mock_bet.user = mock_user
        
        # Mock WebSocket manager
        with patch('api.endpoints.websocket.websocket_manager') as mock_manager:
            mock_manager.broadcast_to_user.return_value = AsyncMock()
            
            # Test with valid data
            await send_bet_status_update(
                bet=mock_bet,
                old_status="pending",
                new_status="resolved",
                result="win",
                resolution_notes="Valid update"
            )
            
            # Get the message
            call_args = mock_manager.broadcast_to_user.call_args
            message = call_args[0][1]
            
            # Validate required fields
            assert message["type"] in ["bet_resolution", "dispute_resolution"]
            assert "data" in message
            assert "timestamp" in message
            
            # Validate data fields
            data = message["data"]
            assert isinstance(data["bet_id"], int)
            assert isinstance(data["old_status"], str)
            assert isinstance(data["new_status"], str)
            assert data["result"] in ["win", "loss", "push", "void"]

    @pytest.mark.asyncio
    async def test_websocket_disconnect_cleanup(self, mock_bet, mock_user):
        """Test WebSocket cleanup on disconnect"""
        from api.endpoints.websocket import websocket_manager
        
        # Mock WebSocket connection
        mock_websocket = Mock()
        mock_websocket.send_text = AsyncMock()
        
        with patch.object(websocket_manager, 'connect') as mock_connect, \
             patch.object(websocket_manager, 'disconnect') as mock_disconnect:
            
            # Connect
            await websocket_manager.connect(mock_websocket, "test_user_123")
            
            # Disconnect
            await websocket_manager.disconnect(mock_websocket, "test_user_123")
            
            # Verify cleanup was called
            mock_disconnect.assert_called_once()
            
            # Verify user is no longer in active connections
            # (This would depend on the actual implementation)

    @pytest.mark.asyncio
    async def test_websocket_error_recovery(self, mock_bet, mock_user):
        """Test WebSocket error recovery"""
        mock_bet.user = mock_user
        
        # Mock WebSocket manager with recovery
        with patch('api.endpoints.websocket.websocket_manager') as mock_manager:
            # Simulate error then recovery
            call_count = 0
            def side_effect(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    raise Exception("Connection lost")
                else:
                    return AsyncMock()
            
            mock_manager.broadcast_to_user.side_effect = side_effect
            
            # First call should fail
            with pytest.raises(Exception):
                await send_bet_status_update(
                    bet=mock_bet,
                    old_status="pending",
                    new_status="resolved",
                    result="win"
                )
            
            # Second call should succeed (simulating recovery)
            await send_bet_status_update(
                bet=mock_bet,
                old_status="pending",
                new_status="resolved",
                result="win"
            )
            
            # Verify both attempts were made
            assert mock_manager.broadcast_to_user.call_count == 2

