# StayEase API Contract

This document outlines the API endpoints for interacting with the StayEase AI Agent.

## 1. Send Message
`POST /api/chat/{conversation_id}/message`

Send a guest message to the AI agent for processing.

### Request Schema
- **Path Parameters**:
  - `conversation_id` (string): Unique identifier for the conversation (thread_id).
- **Body**:
  ```json
  {
    "message": "string"
  }
  ```

### Response Schema
- **Status Code: 200 OK**
  ```json
  {
    "reply": "string"
  }
  ```

### Example
**Request**:
`POST /api/chat/conv_12345/message`
```json
{
  "message": "I need a room in Cox's Bazar for 2 guests on May 1st for 2 nights."
}
```

**Response**:
```json
{
  "reply": "I found a few options for you in Cox's Bazar! The 'Sea View Suite' is available for 5000 BDT per night. Would you like to see more details or book this room?"
}
```

### Error Responses
| Code | Description | Example Body |
|---|---|---|
| 400 | Invalid request body or missing message. | `{"detail": "Message cannot be empty"}` |
| 500 | Internal agent processing error. | `{"detail": "Agent failed to respond"}` |

---

## 2. Get Conversation History
`GET /api/chat/{conversation_id}/history`

Retrieve the full message history for a specific conversation.

### Request Schema
- **Path Parameters**:
  - `conversation_id` (string): Unique identifier for the conversation.

### Response Schema
- **Status Code: 200 OK**
  ```json
  {
    "conversation_id": "string",
    "messages": [
      {
        "role": "guest | agent",
        "content": "string",
        "timestamp": "ISO-8601 string"
      }
    ]
  }
  ```

### Example
**Request**:
`GET /api/chat/conv_12345/history`

**Response**:
```json
{
  "conversation_id": "conv_12345",
  "messages": [
    {
      "role": "guest",
      "content": "I need a room in Cox's Bazar for 2 guests on May 1st for 2 nights.",
      "timestamp": "2026-05-01T10:00:00Z"
    },
    {
      "role": "agent",
      "content": "I found a few options for you in Cox's Bazar! The 'Sea View Suite' is available for 5000 BDT per night. Would you like to see more details or book this room?",
      "timestamp": "2026-05-01T10:00:05Z"
    }
  ]
}
```

### Error Responses
| Code | Description | Example Body |
|---|---|---|
| 404 | Conversation ID not found. | `{"detail": "Conversation not found"}` |
