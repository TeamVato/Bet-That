# Real-Time Bet Resolution Updates

This document describes the implementation of real-time updates and notifications for bet resolutions in the Bet-That platform.

## Overview

The system provides real-time notifications when bets are resolved, disputed, or updated, with both WebSocket connections and polling fallback options.

## Features

### 1. Real-Time Updates
- **WebSocket Connection**: Primary method for real-time updates
- **Polling Fallback**: HTTP endpoint for environments where WebSocket is not available
- **Automatic Reconnection**: WebSocket connections automatically reconnect on failure
- **Connection Status**: Visual indicators show connection status

### 2. Toast Notifications
- **Resolution Notifications**: Toast messages for bet resolutions (win/loss/push/void)
- **Dispute Notifications**: Alerts when bets are disputed
- **Update Notifications**: General bet status updates
- **Action Buttons**: Direct links to view bet details or review disputes

### 3. UI Components
- **BetCard**: Enhanced bet display with resolution status and real-time updates
- **BetList**: Filterable list with status and result filters
- **Recent Resolutions**: Sidebar showing recent resolution activity
- **Connection Status**: Live indicator showing WebSocket connection status

### 4. Email Notifications (Optional)
- **Resolution Emails**: HTML emails sent when bets are resolved
- **Dispute Emails**: Notifications when disputes are raised
- **Configurable**: Can be enabled/disabled via environment variables

## Implementation Details

### Frontend Components

#### WebSocket Hook (`useRealTimeUpdates.ts`)
```typescript
const { isConnected, error, lastMessage } = useRealTimeUpdates(
  userId,
  onBetUpdate
);
```

Features:
- Automatic connection management
- Exponential backoff reconnection
- Message handling and parsing
- Connection status tracking

#### Toast Notification System (`ToastNotification.tsx`)
```typescript
const { notifications, addNotification, removeNotification } = useToastNotifications();
```

Features:
- Multiple notification types (success, error, warning, info)
- Auto-dismiss with configurable duration
- Action buttons for user interaction
- Recent resolutions display

#### Enhanced Bet Components (`BetCard.tsx`)
```typescript
<BetCard 
  bet={bet} 
  onUpdate={handleBetUpdate}
  showActions={true}
/>
```

Features:
- Real-time status updates
- Resolution status badges
- Result indicators
- Action buttons for disputes and resolution

### Backend Implementation

#### WebSocket Endpoint (`websocket.py`)
```python
@router.websocket("/ws/bet-updates")
async def websocket_endpoint(websocket: WebSocket, user_id: Optional[str] = None):
```

Features:
- User-specific filtering
- Connection management
- Message broadcasting
- Status monitoring

#### Polling Endpoint
```python
@router.get("/api/v1/bets/updates")
async def get_bet_updates(since: Optional[str] = None, user_id: Optional[str] = None):
```

Features:
- Timestamp-based filtering
- User-specific updates
- Recent activity retrieval

#### Email Service (`email_service.py`)
```python
def send_bet_resolution_notification(bet: Bet, user: User, result: str):
```

Features:
- HTML email templates
- SMTP configuration
- Error handling
- Optional feature (can be disabled)

## Configuration

### Environment Variables

#### WebSocket Configuration
- No additional configuration required
- Uses existing API_BASE_URL for WebSocket URL

#### Email Configuration (Optional)
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@betthat.com
FROM_NAME=Bet That
```

### Frontend Configuration

#### API Base URL
```typescript
// config/api.ts
export const API_BASE_URL = "http://localhost:8000";
```

#### WebSocket URL
Automatically derived from API_BASE_URL:
- `http://localhost:8000` → `ws://localhost:8000`
- `https://api.betthat.com` → `wss://api.betthat.com`

## Usage Examples

### Basic Real-Time Updates
```typescript
import { useRealTimeUpdates } from '@/hooks/useRealTimeUpdates';

function MyComponent() {
  const handleBetUpdate = (update) => {
    console.log('Bet updated:', update);
    // Update local state, show notifications, etc.
  };

  const { isConnected, error } = useRealTimeUpdates(
    userId,
    handleBetUpdate
  );

  return (
    <div>
      <p>Status: {isConnected ? 'Connected' : 'Disconnected'}</p>
      {error && <p>Error: {error}</p>}
    </div>
  );
}
```

### Toast Notifications
```typescript
import { useToastNotifications, createBetResolutionNotification } from '@/components/Notifications/ToastNotification';

function BetComponent() {
  const { addNotification } = useToastNotifications();

  const handleBetUpdate = (update) => {
    const notification = createBetResolutionNotification(update);
    addNotification(notification);
  };

  return <div>...</div>;
}
```

### Bet List with Filtering
```typescript
import { BetList } from '@/components/BetCard';

function MyBetsPage() {
  const [bets, setBets] = useState([]);

  const handleBetUpdate = (updatedBet) => {
    setBets(prev => prev.map(bet => 
      bet.id === updatedBet.id ? updatedBet : bet
    ));
  };

  return (
    <BetList 
      bets={bets}
      onBetUpdate={handleBetUpdate}
      showFilters={true}
    />
  );
}
```

## API Endpoints

### WebSocket
- **Endpoint**: `/ws/bet-updates`
- **Parameters**: `user_id` (optional)
- **Message Types**: `bet_resolved`, `bet_disputed`, `bet_updated`

### Polling
- **Endpoint**: `/api/v1/bets/updates`
- **Parameters**: `since` (ISO timestamp), `user_id` (optional)
- **Response**: Array of recent updates

### Status
- **Endpoint**: `/ws/status`
- **Response**: Connection statistics and active users

## Message Format

### WebSocket Message
```json
{
  "type": "bet_resolved",
  "bet_id": "123",
  "user_id": "user456",
  "data": {
    "bet_id": "123",
    "status": "settled",
    "result": "win",
    "resolution_notes": "Game completed",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Polling Response
```json
{
  "updates": [
    {
      "type": "bet_resolved",
      "bet_id": "123",
      "user_id": "user456",
      "data": { ... },
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ],
  "last_update": "2024-01-15T10:30:00Z",
  "count": 1
}
```

## Error Handling

### WebSocket Errors
- Connection failures automatically trigger reconnection
- Exponential backoff prevents server overload
- Fallback to polling if WebSocket fails repeatedly

### Email Errors
- Email failures are logged but don't affect bet resolution
- Service gracefully handles missing SMTP configuration

### Frontend Errors
- Toast notifications for connection issues
- Graceful degradation when real-time features fail
- Manual refresh options available

## Testing

### WebSocket Testing
```bash
# Test WebSocket connection
wscat -c ws://localhost:8000/ws/bet-updates?user_id=test123

# Send test message
{"type": "ping"}
```

### Polling Testing
```bash
# Test polling endpoint
curl "http://localhost:8000/api/v1/bets/updates?user_id=test123"

# Test with timestamp
curl "http://localhost:8000/api/v1/bets/updates?since=2024-01-15T10:00:00Z"
```

## Performance Considerations

### WebSocket
- Connection pooling for multiple users
- Message broadcasting efficiency
- Memory management for active connections

### Polling
- Efficient database queries with indexing
- Timestamp-based filtering
- Rate limiting to prevent abuse

### Email
- Asynchronous sending to prevent blocking
- SMTP connection pooling
- Error handling and retry logic

## Security

### WebSocket
- User ID validation
- Message sanitization
- Connection rate limiting

### Email
- SMTP authentication
- Email content validation
- User privacy protection

## Monitoring

### Metrics
- Active WebSocket connections
- Message delivery rates
- Email delivery success rates
- Error rates and types

### Logging
- Connection events
- Message delivery
- Error conditions
- Performance metrics

## Future Enhancements

### Planned Features
- Push notifications for mobile apps
- SMS notifications for critical updates
- Webhook support for external integrations
- Advanced filtering and subscription options

### Performance Improvements
- Redis for message queuing
- Database connection pooling
- Caching for frequently accessed data
- CDN for static assets

## Troubleshooting

### Common Issues

#### WebSocket Connection Fails
1. Check API_BASE_URL configuration
2. Verify WebSocket support in browser
3. Check network connectivity
4. Review server logs for errors

#### Email Notifications Not Working
1. Verify SMTP configuration
2. Check email service logs
3. Test SMTP connection manually
4. Verify user email addresses

#### Real-Time Updates Not Appearing
1. Check WebSocket connection status
2. Verify user ID filtering
3. Check browser console for errors
4. Test polling endpoint directly

### Debug Mode
Enable debug logging by setting:
```bash
LOG_LEVEL=DEBUG
```

This will provide detailed information about:
- WebSocket connections
- Message delivery
- Email sending
- Error conditions

