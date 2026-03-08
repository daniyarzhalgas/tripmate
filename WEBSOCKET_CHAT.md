# WebSocket Chat Documentation

## Overview

The chat system now supports real-time messaging via WebSockets. Users can connect to a chat group and send/receive messages instantly without polling.

## WebSocket Endpoint

```
ws://your-host/api/v1/chats/ws/{chat_group_id}?token=YOUR_JWT_TOKEN
```

## Authentication

Pass your JWT access token as a query parameter when connecting:

```
ws://localhost:8000/api/v1/chats/ws/1?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Message Types

### Messages You Send

#### 1. Send a Chat Message

```json
{
  "type": "message",
  "content": "Hello, everyone!"
}
```

#### 2. Send Typing Indicator

```json
{
  "type": "typing",
  "is_typing": true
}
```

### Messages You Receive

#### 1. Connection Established

```json
{
  "type": "connection",
  "status": "connected",
  "chat_group_id": 1,
  "timestamp": "2026-03-06T10:30:00"
}
```

#### 2. New Message

```json
{
  "type": "message",
  "id": 42,
  "chat_group_id": 1,
  "sender_id": 5,
  "content": "Hello, everyone!",
  "created_at": "2026-03-06T10:30:15"
}
```

#### 3. Typing Indicator

```json
{
  "type": "typing",
  "user_id": 5,
  "is_typing": true,
  "timestamp": "2026-03-06T10:30:10"
}
```

#### 4. User Joined

```json
{
  "type": "user_joined",
  "user_id": 7,
  "timestamp": "2026-03-06T10:31:00"
}
```

#### 5. User Left

```json
{
  "type": "user_left",
  "user_id": 7,
  "timestamp": "2026-03-06T10:35:00"
}
```

#### 6. Error Message

```json
{
  "type": "error",
  "message": "Failed to send message"
}
```

## JavaScript Example

```javascript
// Get JWT token from your login response
const token = "your_jwt_token_here";
const chatGroupId = 1;

// Connect to WebSocket
const ws = new WebSocket(
  `ws://localhost:8000/api/v1/chats/ws/${chatGroupId}?token=${token}`,
);

// Handle connection open
ws.onopen = () => {
  console.log("Connected to chat");
};

// Handle incoming messages
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  switch (data.type) {
    case "connection":
      console.log("Successfully connected to chat group", data.chat_group_id);
      break;

    case "message":
      console.log(`Message from user ${data.sender_id}: ${data.content}`);
      // Display message in your UI
      break;

    case "typing":
      if (data.is_typing) {
        console.log(`User ${data.user_id} is typing...`);
      } else {
        console.log(`User ${data.user_id} stopped typing`);
      }
      break;

    case "user_joined":
      console.log(`User ${data.user_id} joined the chat`);
      break;

    case "user_left":
      console.log(`User ${data.user_id} left the chat`);
      break;

    case "error":
      console.error("Error:", data.message);
      break;
  }
};

// Handle errors
ws.onerror = (error) => {
  console.error("WebSocket error:", error);
};

// Handle connection close
ws.onclose = (event) => {
  console.log("Disconnected from chat", event.code, event.reason);
};

// Send a message
function sendMessage(content) {
  const message = {
    type: "message",
    content: content,
  };
  ws.send(JSON.stringify(message));
}

// Send typing indicator
function sendTypingIndicator(isTyping) {
  const indicator = {
    type: "typing",
    is_typing: isTyping,
  };
  ws.send(JSON.stringify(indicator));
}

// Usage examples
sendMessage("Hello, everyone!");
sendTypingIndicator(true); // Start typing
// ... user is typing ...
sendTypingIndicator(false); // Stop typing
```

## Python Client Example

```python
import asyncio
import websockets
import json

async def chat_client(token: str, chat_group_id: int):
    uri = f"ws://localhost:8000/api/v1/chats/ws/{chat_group_id}?token={token}"

    async with websockets.connect(uri) as websocket:
        print("Connected to chat")

        # Receive messages
        async def receive_messages():
            async for message in websocket:
                data = json.loads(message)
                print(f"Received: {data}")

        # Send a message
        async def send_message(content: str):
            message = {
                "type": "message",
                "content": content
            }
            await websocket.send(json.stringify(message))

        # Run both send and receive
        await asyncio.gather(
            receive_messages(),
            send_message("Hello from Python!")
        )

# Run the client
asyncio.run(chat_client("your_jwt_token", 1))
```

## REST API Endpoints (Still Available)

You can still use the REST API for:

- Fetching message history: `GET /api/v1/chats/{chat_group_id}/messages`
- Getting recent messages: `GET /api/v1/chats/{chat_group_id}/messages/recent`
- Viewing chat groups: `GET /api/v1/chats/my-groups`
- Getting active users: `GET /api/v1/chats/{chat_group_id}/active-users`
- Deleting messages: `DELETE /api/v1/chats/{chat_group_id}/messages/{message_id}`

## Features

✅ Real-time message delivery
✅ Typing indicators
✅ User join/leave notifications
✅ JWT authentication
✅ Multiple users per chat group
✅ Persistent message storage
✅ Active user tracking
✅ Automatic reconnection handling (client-side)

## How It Works

1. **Trip Vacancy Created** → Chat group automatically created with owner as first member
2. **Offer Accepted** → User automatically added to chat group
3. **Users Connect** → WebSocket connection established for real-time communication
4. **Messages Sent** → Saved to database AND broadcast to all connected users
5. **Users Disconnect** → Other members notified

## Security

- JWT authentication required for WebSocket connections
- Users must be members of the chat group to connect
- Messages are validated and sanitized
- Token expiration is enforced
- Blacklisted tokens are rejected

## Error Handling

WebSocket will close with specific codes:

- `1008` - Policy violation (invalid token or not a member)
- `1011` - Internal error

## Testing

You can test WebSocket connections using:

- Browser console (JavaScript)
- Postman (supports WebSocket)
- wscat: `npm install -g wscat`
- Python websockets library
- Any WebSocket client

Example with wscat:

```bash
wscat -c "ws://localhost:8000/api/v1/chats/ws/1?token=YOUR_TOKEN"
# Then send: {"type": "message", "content": "Hello!"}
```
