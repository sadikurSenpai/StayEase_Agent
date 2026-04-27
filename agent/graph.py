from __future__ import annotations

from typing import Literal

from langchain_core.messages import AIMessage
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from agent.nodes import call_agent, classify_intent, escalate
from agent.state import AgentState
from agent.tools import TOOLS


#  Conditional routing functions 

def route_after_classify(
    state: AgentState,
) -> Literal["call_agent", "escalate"]:
    """Route to escalate when intent is out-of-scope; otherwise enter the ReAct loop."""
    if state.get("intent") == "escalate":
        return "escalate"
    return "call_agent"


def route_after_agent(
    state: AgentState,
) -> Literal["run_tools", "__end__"]:
    """Route to run_tools when the agent produced tool_calls; otherwise end the graph."""
    messages = state.get("messages", [])
    if not messages:
        return "__end__"
    last = messages[-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "run_tools"
    return "__end__"


#  Graph construction 

builder = StateGraph(AgentState)

builder.add_node("classify_intent", classify_intent)
builder.add_node("call_agent", call_agent)
builder.add_node("run_tools", ToolNode(TOOLS))  # executes tool_calls from call_agent
builder.add_node("escalate", escalate)

builder.add_edge(START, "classify_intent")

builder.add_conditional_edges(
    "classify_intent",
    route_after_classify,
    {"call_agent": "call_agent", "escalate": "escalate"},
)

builder.add_conditional_edges(
    "call_agent",
    route_after_agent,
    {"run_tools": "run_tools", "__end__": END},
)

builder.add_edge("run_tools", "call_agent")  # ReAct loop
builder.add_edge("escalate", END)

# TODO: replace with builder.compile(checkpointer=PostgresSaver(conn)) once
#       the PostgresSaver is wired to the AsyncSession from database.py
graph = builder.compile()