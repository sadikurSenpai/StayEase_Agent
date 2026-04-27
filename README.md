# StayEase AI Agent

## Project Structure

```
StayEase_Agent/
├── agent/
│   ├── __init__.py
│   ├── graph.py      # Graph construction & routing
│   ├── nodes.py      # Node functions (classify, agent, escalate)
│   ├── state.py      # TypedDict state definition
│   └── tools.py      # search, details, and booking tools
├── routers/
│   ├── __init__.py
│   └── chat.py       # API endpoints (message, history)
├── schemas.py        # Pydantic models for API
├── database.py       # SQLAlchemy engine & session
├── models.py         # SQLAlchemy DB models (Listings, Bookings, Conversations)
├── init_db.py        # DB initialization & seeding logic
├── main.py           # FastAPI application entry point
├── test_vision.py    # End-to-end validation script
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── api.md            # API Contract documentation
└── README.md         # Architecture & setup guide
```

---

## 1. Architecture Document

### 1.1 System Overview

StayEase AI Agent is a conversational booking assistant that handles three guest intents: searching for available properties, retrieving listing details, and creating bookings. A FastAPI backend receives guest messages over HTTP and delegates each message to a LangGraph agent. The agent classifies the intent, calls the appropriate database-backed tool via a ReAct loop, and returns a natural-language reply. 

> [!IMPORTANT]
> **End-to-End Implementation**: While the task requirements specify an architectural design, this project is **fully functional**. It includes a complete backend stack with a persistent PostgreSQL database and an automated test suite.

```mermaid
graph TD
    %% Main Nodes
    Start((START))
    End((END))
    
    Classify["<b>classify_intent</b><br/><i>Node: Identifies guest goal</i>"]
    Agent["<b>agent_node</b><br/><i>Node: LLM Reasoning (ReAct)</i>"]
    Tools["<b>tool_node</b><br/><i>Node: Executes search/details/book</i>"]
    Escalate["<b>escalate_node</b><br/><i>Node: Handles out-of-scope</i>"]

    %% Graph Flow & Conditional Routing
    Start --> Classify
    
    Classify --> RouteIntent{route_intent}
    RouteIntent -- "search / details / book" --> Agent
    RouteIntent -- "escalate" --> Escalate

    %% ReAct Loop logic
    Agent --> ToolsCondition{tools_condition}
    ToolsCondition -- "continue (tool call)" --> Tools
    ToolsCondition -- "end (final response)" --> End
    
    %% Loop back
    Tools --> Agent

    %% Terminal nodes
    Escalate --> End

    %% External Systems subgraph
    subgraph "External Integrations"
        direction LR
        LLM[("<b>Groq / OpenRouter</b><br/>(LLM Reasoning)")]
        DB[(<b>PostgreSQL</b><br/>(Listing & Booking Data))]
    end

    %% Interaction links
    Classify -.-> LLM
    Agent -.-> LLM
    Tools -.-> DB
```

---

### 1.2 Conversation Flow

1. **Message Received**: A guest says: "I need a room in Cox's Bazar for 2 nights for 2 guests starting tomorrow."
2. **Intent Classification**: The `classify_intent` node detects a `search` intent based on the request for a room and location.
3. **Tool Execution**: The `agent_node` triggers the `search_available_properties` tool with parameters: `location="Cox's Bazar"`, `guests=2`, and calculated dates.
4. **Database Query**: The tool queries the `listings` table for available properties in Cox's Bazar that can accommodate 2 guests.
5. **Response Generation**: The `agent_node` receives the list of properties (e.g., "Sea View Suite - 5000 BDT/night") and generates a friendly response listing the options.
6. **Result**: The guest receives: "I found 3 properties in Cox's Bazar! The 'Sea View Suite' is available for 5000 BDT per night. Would you like more details on any of these?"

---

### 1.3 LangGraph State Design

```python
class AgentState(TypedDict):
    messages:        Annotated[list[BaseMessage], add_messages]
    conversation_id: str
    intent:          Literal["search", "details", "book", "escalate"] | None
```

| Field | Type | Why it is needed |
| :--- | :--- | :--- |
| `messages` | `list[BaseMessage]` | Maintains the full conversation history to support context-aware multi-turn dialogues. |
| `conversation_id` | `str` | Used as a unique thread identifier to load and save conversation state across requests. |
| `intent` | `Literal[...]` | Stores the classified intent to guide conditional routing without re-analyzing the message list. |

---

## 1.4 Node Design

| Node | What it does | What it updates in state | Next Node |
| :--- | :--- | :--- | :--- |
| `classify_intent` | Categorizes the user's message into one of four predefined intents. | `intent` | `agent_node` or `escalate_node` |
| `agent_node` | Decides whether to call a database tool or reply directly to the guest. | `messages` | `tool_node` or `__end__` |
| `tool_node` | Executes the requested database tool (search, details, or book) and returns results. | `messages` | `agent_node` |
| `escalate_node` | Politely informs the guest that a human representative is required for their request. | `messages` | `__end__` |

---

## 1.5 Tool Definitions

| Tool | Input Parameters | Output Format | When used |
| :--- | :--- | :--- | :--- |
| `search_available_properties` | `location` (str), `check_in` (str), `check_out` (str), `guests` (int) | JSON list of available listings with IDs and prices. | When guest searches for rooms or availability. |
| `get_listing_details` | `listing_id` (int) | JSON object with full description, amenities, and location. | When guest asks for details on a specific property. |
| `create_booking` | `listing_id` (int), `guest_name` (str), `check_in` (str), `check_out` (str) | JSON confirmation with a `booking_id` and total price. | When guest confirms they want to book a room. |

---

### 1.6 Database Schema Design

#### `listings`
| Column | Type | Notes |
| :--- | :--- | :--- |
| `id` | `SERIAL` PK | Unique identifier for each property. |
| `name` | `VARCHAR(255)` | Name of the listing. |
| `location` | `VARCHAR(100)` | City or area in Bangladesh. |
| `price_per_night` | `INTEGER` | Amount in BDT. |
| `description` | `TEXT` | Full property description. |
| `max_guests` | `INTEGER` | Maximum occupancy allowed. |
| `available` | `BOOLEAN` | Boolean flag for general availability. |

#### `bookings`
| Column | Type | Notes |
| :--- | :--- | :--- |
| `id` | `SERIAL` PK | Unique identifier for the reservation. |
| `listing_id` | `INTEGER` FK | Reference to the `listings.id`. |
| `guest_name` | `VARCHAR(255)` | Full name of the booking guest. |
| `check_in` | `DATE` | Reservation start date. |
| `check_out` | `DATE` | Reservation end date. |
| `total_price` | `INTEGER` | Calculated total cost in BDT. |
| `status` | `VARCHAR(50)` | Default is `'confirmed'`. |

#### `conversations`
| Column | Type | Notes |
| :--- | :--- | :--- |
| `id` | `SERIAL` PK | Unique record ID. |
| `thread_id` | `VARCHAR(255)` | Unique identifier matching `conversation_id`. |
| `checkpoint_data` | `TEXT` | Serialized LangGraph state or conversation metadata. |
| `updated_at` | `TIMESTAMP` | Auto-updated timestamp of the last message. |

---

## 2. API Contract
The full API documentation, including request/response schemas and realistic Bangladeshi examples, can be found in **[api.md](file:///home/md-shadikur-rahman-sheam/DataCrata_new/StayEase_Agent/api.md)**.

---

## 3. Quick Start (Build & Test)

Follow these steps to build the system and verify the end-to-end functionality:

### Step 1: Build and Run
Build the environment and start the services in detached mode:
```bash
docker compose up --build -d
```

### Step 2: Run the Vision Test
Execute the end-to-end test script to simulate a guest conversation (Search -> Details -> Book -> Escalate):
```bash
python3 test_vision.py
```

### Step 3: Verify Database Updates
Check that the agent successfully updated both the business logic (**bookings**) and the conversation state (**conversations**):
```bash
# Verify the new booking exists
docker exec -it stayease_db_container psql -U stayease_user -d stayease_db -c "SELECT * FROM bookings;"

# Verify the conversation history was persisted
docker exec -it stayease_db_container psql -U stayease_user -d stayease_db -c "SELECT * FROM conversations;"
```



