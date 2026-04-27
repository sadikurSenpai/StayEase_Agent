# StayEase API Documentation 

Welcome to the StayEase API. This document explains how you can talk to our AI booking assistant. It’s pretty straightforward—you send a message, the agent thinks and talks to the database, and then gives you a reply. We’ve also got a way for you to pull up the whole chat history if you need to.

---

## 1. Chat with the Agent
`POST /api/chat/{conversation_id}/message`

This is where all the magic happens. When a guest types something, you send it here. The agent will figure out if they're looking for a beach house in Cox's Bazar, asking about prices in Sylhet, or ready to book a stay at Saint Martin.

### What you need to send (Request)
- **Path Parameter**: 
  - `conversation_id`: A unique string for the session (like `conv_789`). This helps the agent remember what was said before in the same chat.
- **JSON Body**:
  ```json
  {
    "content": "I'm looking for a room in Cox's Bazar for 2 people, starting tomorrow for 3 nights."
  }
  ```

### What the agent sends back (Response)
- **Status**: `200 OK`
- **JSON Body**:
  ```json
  {
    "conversation_id": "conv_789",
    "role": "assistant",
    "content": "I found some great options for you! The 'Sea View Suite' is available for 5000 BDT per night. It's got a beautiful view of the Bay of Bengal. Would you like to know more about it?"
  }
  ```

### If something goes wrong (Errors)
- **400 Bad Request**: Usually happens if the message is empty.
  - `{"detail": "Message cannot be empty"}`
- **500 Server Error**: If our AI agent hits a snag or the database is being slow.
  - `{"detail": "Agent error: [specific error message]"}`

---

## 2. Get the Chat History
`GET /api/chat/{conversation_id}/history`

If your app needs to reload the chat or show the guest what they talked about earlier, use this endpoint. It pulls everything from the database—both what the user said and how the agent replied.

### What you need to send (Request)
- **Path Parameter**: 
  - `conversation_id`: The ID of the chat you want to retrieve.

### What you get back (Response)
- **Status**: `200 OK`
- **JSON Body**:
  ```json
  {
    "conversation_id": "conv_789",
    "messages": [
      {
        "role": "user",
        "content": "I'm looking for a room in Cox's Bazar for 2 people...",
        "timestamp": "2026-05-01T10:00:00Z"
      },
      {
        "role": "assistant",
        "content": "I found some great options for you! The 'Sea View Suite' is available for 5000 BDT per night...",
        "timestamp": "2026-05-01T10:00:05Z"
      }
    ]
  }
  ```

### If the chat isn't there (Errors)
- **404 Not Found**: If you ask for a `conversation_id` that doesn't exist yet.
  - `{"detail": "Conversation not found"}`
- **500 Server Error**: If we can't talk to the database.
  - `{"detail": "History error: [specific error message]"}`

---

> [!TIP]
> All prices are handled in **BDT** (Bangladeshi Taka). When the agent talks about locations like Cox's Bazar, Sylhet, or Saint Martin, it's pulling real-time data from our `listings` table.
