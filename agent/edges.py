from langgraph.graph import END

def should_continue(state):
    """Quyết định: Đi tiếp sang Tools hay Kết thúc."""
    last_message = state['messages'][-1]
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    return END