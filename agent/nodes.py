from __future__ import annotations

from langchain_core.messages import AIMessage

from agent.state import AgentState


def classify_intent(state: AgentState) -> dict:
    """Read the last HumanMessage and classify it into one of four intents.

    Updates: intent
    Next: call_agent (search / details / book) or escalate
    """
    # TODO: lightweight LLM call with a short classification prompt —
    #   last_message = state["messages"][-1].content
    #   response = llm.invoke(CLASSIFY_PROMPT.format(message=last_message))
    #   return {"intent": response.content.strip()}
    return {"intent": "search"}  # placeholder: real LLM call replaces this


def call_agent(state: AgentState) -> dict:
    """Run the ReAct LLM with all three tools bound.

    Produces an AIMessage — with tool_calls when a DB lookup is needed,
    or a plain final answer when enough information has been gathered.

    Updates: messages
    Next: run_tools (tool_calls present) or END (no tool_calls)
    """
    # TODO: bind tools to LLM and invoke with full message history —
    #   llm_with_tools = llm.bind_tools(TOOLS)
    #   response = llm_with_tools.invoke(state["messages"])
    #   return {"messages": [response]}
    return {"messages": [AIMessage(content="[agent placeholder — LLM not wired yet]")]}


def escalate(state: AgentState) -> dict:
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