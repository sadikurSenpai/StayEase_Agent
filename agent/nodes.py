from __future__ import annotations

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from agent.state import AgentState
from agent.tools import TOOLS

load_dotenv()

#  LLM instances

_llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
_llm_with_tools = _llm.bind_tools(TOOLS)

#  Prompts 

_CLASSIFY_SYSTEM = SystemMessage(
    content=(
        "You are an intent classifier for a hotel booking assistant. "
        "Classify the user message into exactly one of these four intents:\n"
        "  search   — user wants to find available properties\n"
        "  details  — user wants details about a specific property\n"
        "  book     — user wants to make a booking\n"
        "  escalate — anything outside the above three\n\n"
        "Reply with the single word only. No punctuation, no explanation."
    )
)

_AGENT_SYSTEM = SystemMessage(
    content=(
        "You are StayEase, a helpful accommodation booking assistant for Bangladesh. "
        "Help guests search for properties, get listing details, and make bookings. "
        "Use the available tools to fulfil every request — never answer from memory.\n\n"
        "Tool usage rules:\n"
        "- search_available_properties: use when the guest asks to find or list properties.\n"
        "- get_listing_details: use when the guest asks about a specific property. "
        "Pass listing_name when the guest refers to a property by name; "
        "pass listing_id only if you already have it from a previous search result.\n"
        "- create_booking: use when the guest confirms they want to book. "
        "If you do not yet have the listing_id, call search_available_properties first.\n\n"
        "Always respond in a friendly tone and quote prices in BDT (Bangladeshi Taka, ৳)."
    )
)

_VALID_INTENTS = {"search", "details", "book", "escalate"}

#  Node functions 

def classify_intent(state: AgentState) -> dict:
    """Read the last HumanMessage and classify it into one of four intents.

    Updates: intent
    Next: call_agent (search / details / book) or escalate
    """
    last_content = state["messages"][-1].content
    response = _llm.invoke([_CLASSIFY_SYSTEM, HumanMessage(content=last_content)])
    raw = response.content.strip().lower()
    intent = raw if raw in _VALID_INTENTS else "escalate"
    return {"intent": intent}


def call_agent(state: AgentState) -> dict:
    """Run the ReAct LLM with all three tools bound.

    Injects a system message at invocation time so it does not accumulate in
    state across turns. Produces an AIMessage with tool_calls when a DB lookup
    is needed, or a plain final answer when enough information is gathered.

    Updates: messages
    Next: run_tools (tool_calls present) or END (no tool_calls)
    """
    messages = [_AGENT_SYSTEM, *state["messages"]]
    response = _llm_with_tools.invoke(messages)
    return {"messages": [response]}


def escalate(_state: AgentState) -> dict:
    """Append a canned escalation message for out-of-scope requests.

    Updates: messages
    Next: END
    """
    msg = AIMessage(
        content=(
            "I can only help with searching properties, viewing listing details, "
            "and making bookings. For anything else, I am connecting you to a "
            "human agent who will follow up shortly."
        )
    )
    return {"messages": [msg]}
