"""
WebSocket endpoints for real-time bet updates
"""

import json
import logging
from typing import Dict, List, Optional, Set
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Bet, BetStatus
from ..services.bet_service import BetService
from ..repositories.bet_repository import BetRepository

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer(auto_error=False)

# Store active WebSocket connections
class ConnectionManager:
    def __init__(self):
        # Dictionary to store connections by user_id
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # Dictionary to store connections by connection_id for cleanup
        self.connection_ids: Dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        
        self.active_connections[user_id].append(websocket)
        self.connection_ids[websocket] = user_id
        
        logger.info(f"WebSocket connected for user {user_id}. Total connections: {len(self.active_connections[user_id])}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.connection_ids:
            user_id = self.connection_ids[websocket]
            
            if user_id in self.active_connections:
                self.active_connections[user_id].remove(websocket)
                
                # Remove user entry if no more connections
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
            
            del self.connection_ids[websocket]
            
            logger.info(f"WebSocket disconnected for user {user_id}")

    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            # Send to all connections for this user
            for connection in self.active_connections[user_id][:]:  # Copy list to avoid modification during iteration
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error sending message to user {user_id}: {e}")
                    # Remove broken connection
                    self.disconnect(connection)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected users"""
        for user_id, connections in self.active_connections.items():
            await self.send_personal_message(message, user_id)

    def get_connection_count(self) -> int:
        return sum(len(connections) for connections in self.active_connections.values())

    def get_user_connection_count(self, user_id: str) -> int:
        return len(self.active_connections.get(user_id, []))

# Global connection manager
manager = ConnectionManager()

@router.websocket("/ws/bet-updates")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: Optional[str] = Query(None, description="User ID for filtering updates")
):
    """
    WebSocket endpoint for real-time bet updates
    
    Query parameters:
    - user_id: Optional user ID to filter updates for specific user
    """
    await manager.connect(websocket, user_id or "anonymous")
    
    try:
        # Send initial connection confirmation
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "message": "Connected to bet updates",
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }))
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for messages from client (ping/pong, etc.)
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }))
                elif message.get("type") == "subscribe":
                    # Handle subscription to specific bet types or events
                    await websocket.send_text(json.dumps({
                        "type": "subscription_confirmed",
                        "subscription": message.get("subscription", {}),
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }))
                    
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }))
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Internal server error",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }))
                
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)

@router.get("/ws/status")
async def websocket_status():
    """Get WebSocket connection status"""
    return {
        "total_connections": manager.get_connection_count(),
        "active_users": len(manager.active_connections),
        "connections_by_user": {
            user_id: manager.get_user_connection_count(user_id)
            for user_id in manager.active_connections.keys()
        }
    }

@router.get("/api/v1/bets/updates")
async def get_bet_updates(
    since: Optional[str] = Query(None, description="ISO timestamp to get updates since"),
    user_id: Optional[str] = Query(None, description="User ID to filter updates"),
    db: Session = Depends(get_db)
):
    """
    Polling endpoint for bet updates (fallback when WebSocket is not available)
    
    Returns recent bet updates for the specified user since the given timestamp.
    """
    from ..models import Bet, BetResolutionHistory
    from datetime import datetime, timezone
    
    # Parse since timestamp
    since_dt = None
    if since:
        try:
            since_dt = datetime.fromisoformat(since.replace('Z', '+00:00'))
        except ValueError:
            return {"error": "Invalid timestamp format", "updates": [], "last_update": None}
    
    # Build query
    query = db.query(Bet).join(BetResolutionHistory, Bet.id == BetResolutionHistory.bet_id)
    
    if user_id:
        query = query.filter(Bet.external_user_id == user_id)
    
    if since_dt:
        query = query.filter(BetResolutionHistory.created_at > since_dt)
    
    # Get recent updates
    recent_bets = query.order_by(BetResolutionHistory.created_at.desc()).limit(50).all()
    
    # Format updates
    updates = []
    for bet in recent_bets:
        # Get latest resolution history entry
        latest_history = db.query(BetResolutionHistory)\
            .filter(BetResolutionHistory.bet_id == bet.id)\
            .order_by(BetResolutionHistory.created_at.desc())\
            .first()
        
        if latest_history:
            update_data = {
                "bet_id": str(bet.id),
                "status": bet.status,
                "result": getattr(bet, 'result', None),
                "resolution_notes": latest_history.resolution_notes,
                "resolution_source": latest_history.resolution_source,
                "dispute_reason": latest_history.dispute_reason,
                "updated_at": latest_history.created_at.isoformat()
            }
            
            # Determine update type
            if latest_history.action_type == "resolve":
                update_type = "bet_resolved"
            elif latest_history.action_type == "dispute":
                update_type = "bet_disputed"
            else:
                update_type = "bet_updated"
            
            updates.append({
                "type": update_type,
                "bet_id": str(bet.id),
                "user_id": str(bet.external_user_id) if bet.external_user_id else "anonymous",
                "data": update_data,
                "timestamp": latest_history.created_at.isoformat()
            })
    
    # Get last update timestamp
    last_update = None
    if updates:
        last_update = max(update["timestamp"] for update in updates)
    
    return {
        "updates": updates,
        "last_update": last_update,
        "count": len(updates)
    }

# Function to send bet resolution updates
async def send_bet_resolution_update(
    bet_id: str,
    user_id: str,
    update_type: str,
    data: dict
):
    """Send bet resolution update to connected clients"""
    message = {
        "type": update_type,
        "bet_id": bet_id,
        "user_id": user_id,
        "data": data,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # Send to specific user if user_id provided
    if user_id and user_id != "anonymous":
        await manager.send_personal_message(message, user_id)
    else:
        # Broadcast to all connected users
        await manager.broadcast(message)
    
    logger.info(f"Sent {update_type} update for bet {bet_id} to user {user_id}")

# Function to send bet status updates
async def send_bet_status_update(
    bet: Bet,
    old_status: str,
    new_status: str,
    result: Optional[str] = None,
    resolution_notes: Optional[str] = None
):
    """Send bet status update to connected clients"""
    # Get user_id from bet
    user_id = str(bet.external_user_id) if bet.external_user_id else "anonymous"
    
    update_data = {
        "bet_id": str(bet.id),
        "status": new_status,
        "previous_status": old_status,
        "result": result,
        "resolution_notes": resolution_notes,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Determine update type based on status change
    if new_status == BetStatus.SETTLED:
        update_type = "bet_resolved"
    elif new_status == "disputed":
        update_type = "bet_disputed"
    else:
        update_type = "bet_updated"
    
    await send_bet_resolution_update(
        bet_id=str(bet.id),
        user_id=user_id,
        update_type=update_type,
        data=update_data
    )

# Function to send dispute resolution updates
async def send_dispute_resolution_update(
    bet: Bet,
    dispute_reason: str,
    resolution_result: Optional[str] = None
):
    """Send dispute resolution update to connected clients"""
    user_id = str(bet.external_user_id) if bet.external_user_id else "anonymous"
    
    update_data = {
        "bet_id": str(bet.id),
        "status": bet.status,
        "dispute_reason": dispute_reason,
        "resolution_result": resolution_result,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await send_bet_resolution_update(
        bet_id=str(bet.id),
        user_id=user_id,
        update_type="dispute_resolved",
        data=update_data
    )

# Export the manager for use in other modules
__all__ = ["router", "manager", "send_bet_resolution_update", "send_bet_status_update", "send_dispute_resolution_update"]
