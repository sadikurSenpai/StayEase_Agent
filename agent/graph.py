from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from .state import AgentState
from .nodes import classify_intent, agent_node, escalate_node
from .tools import search_available_properties, get_listing_details, create_booking

def route_intent(state: AgentState) -> str:
    """Route to agent or escalate based on intent."""
    intent = state.get("intent")
    if intent == "escalate":
        return "escalate_node"
    return "agent_node"

def build_graph() -> StateGraph:
    """
    Constructs the LangGraph state graph for the StayEase agent.
    """
    workflow = StateGraph(AgentState)
    
    # Define tools and tool node
    tools = [search_available_properties, get_listing_details, create_booking]
    tool_node = ToolNode(tools)
    
    # Add nodes
    workflow.add_node("classify_intent", classify_intent)
    workflow.add_node("agent_node", agent_node)
    workflow.add_node("tool_node", tool_node)
    workflow.add_node("escalate_node", escalate_node)
    
    # Add edges
    workflow.add_edge(START, "classify_intent")
    
    # Conditional routing after intent classification
    workflow.add_conditional_edges("classify_intent", route_intent)
    
    # Prebuilt routing for agent node to tools
    workflow.add_conditional_edges(
        "agent_node",
        tools_condition,
        {"tools": "tool_node", END: END}
    )
    
    # After tools are done, return to agent
    workflow.add_edge("tool_node", "agent_node")
    
    # Escalation goes to END
    workflow.add_edge("escalate_node", END)
    
    return workflow.compile()

graph = build_graph()
