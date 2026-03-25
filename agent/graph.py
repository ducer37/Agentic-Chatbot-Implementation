from langgraph.graph import StateGraph
from agent.state import AgentState
from agent.nodes import call_model, tool_node
from agent.edges import should_continue
from functools import partial

def create_graph(mcp_helper, tools, checkpointer):
    workflow = StateGraph(AgentState)

    # Sử dụng partial để truyền thêm tham số (mcp_helper, tools) vào Nodes
    workflow.add_node("agent", partial(call_model, tools=tools))
    workflow.add_node("tools", partial(tool_node, mcp_helper=mcp_helper))

    workflow.set_entry_point("agent")
    workflow.add_conditional_edges("agent", should_continue)
    workflow.add_edge("tools", "agent")

    return workflow.compile(checkpointer=checkpointer)