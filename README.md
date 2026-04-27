# StayEase AI Agent

## Project Structure

```
StayEase_Agent/
├── agent/
│   ├── __init__.py
│   ├── graph.py
│   ├── nodes.py
│   ├── state.py
│   └── tools.py
├── routers/
│   ├── __init__.py
│   └── chat.py
├── schemas.py
├── database.py
├── models.py
├── main.py
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── api.md
└── README.md
```

---

## 1. Architecture Document

### 1.1 System Overview

StayEase AI Agent is a conversational booking assistant that handles three guest intents: searching for available properties, retrieving listing details, and creating bookings. A FastAPI backend receives guest messages over HTTP and delegates each message to a LangGraph agent. The agent classifies the intent, calls the appropriate database-backed tool via a ReAct loop, and returns a natural-language reply. All conversation state is persisted in PostgreSQL through LangGraph's `PostgresSaver` checkpointer, keyed by `conversation_id`.



#### need mermaid later



---

### 1.2 Database Schema 
The database is standardized and normalized solely for the perspective of the features mentioned only. If there are other features

#### `listings`
| Column | Type | Notes |
|---|---|---|
| `id` | `SERIAL` PK | |
| `name` | `VARCHAR(255)` NOT NULL | |
| `location` | `VARCHAR(100)` NOT NULL | |
| `price_per_night` | `INTEGER` NOT NULL | Amount in BDT |
| `description` | `TEXT` | |
| `max_guests` | `INTEGER` NOT NULL | |
| `available` | `BOOLEAN` DEFAULT `TRUE` | |

#### `bookings`
| Column | Type | Notes |
|---|---|---|
| `id` | `SERIAL` PK | |
| `listing_id` | `INTEGER` FK → `listings.id` | |
| `guest_name` | `VARCHAR(255)` NOT NULL | |
| `check_in` | `DATE` NOT NULL | |
| `check_out` | `DATE` NOT NULL | |
| `total_price` | `INTEGER` NOT NULL | Amount in BDT |
| `status` | `VARCHAR(50)` DEFAULT `'confirmed'` | |

#### `conversations`
| Column | Type | Notes |
|---|---|---|
| `id` | `SERIAL` PK | |
| `thread_id` | `VARCHAR(255)` UNIQUE NOT NULL | Matches `conversation_id` from the API |
| `checkpoint_data` | `BYTEA` | Serialized LangGraph state written by `PostgresSaver` |
| `updated_at` | `TIMESTAMP` DEFAULT `CURRENT_TIMESTAMP` | |


---

### 1.3 LangGraph State Design

```python
class AgentState(TypedDict):
    messages:        Annotated[list[BaseMessage], add_messages]
    conversation_id: str
    intent:          Literal["search", "details", "book", "escalate"] | None
```

| Field | Type | Why it is needed |
|---|---|---|
| `messages` | `Annotated[list[BaseMessage], add_messages]` | Holds the full conversation. The `add_messages` reducer appends rather than replaces, which is required for LangGraph checkpointing and the ReAct loop to work correctly. |
| `conversation_id` | `str` | Passed as `thread_id` into the `PostgresSaver` config so state is loaded and saved per-conversation across HTTP requests. |
| `intent` | `Literal[...] \| None` | Set once by `classify_intent` and read by the conditional edge that follows. Avoids re-parsing the message list in the routing function. `None` only at graph start before classification. |

---

