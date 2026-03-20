import os
from langchain_groq import ChatGroq
from langchain_core.messages import ToolMessage
from agent.prompts import SYSTEM_PROMPT
from dotenv import load_dotenv

load_dotenv()


# Khởi tạo LLM
llm = ChatGroq(model=os.getenv("MODEL"), api_key=os.getenv("GROQ_API_KEY"))

async def call_model(state, tools):
    """Node suy nghĩ: Quyết định dùng tool hay trả lời."""
    messages = state['messages'][-10:]
    # Chèn System Prompt nếu là tin nhắn đầu tiên
    if not messages or messages[0].type != "system":
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + list(messages)
    
    # Gắn tools vào model và gọi
    llm_with_tools = llm.bind_tools(tools)
    response = await llm_with_tools.ainvoke(messages)
    return {"messages": [response]}

async def tool_node(state, mcp_helper):
    """Node hành động: Thực thi các MCP Tools."""
    last_message = state['messages'][-1]
    results = []
    
    for tool_call in last_message.tool_calls:
        print(f"⚙️  LangGraph thực thi: {tool_call['name']}...")
        # Gọi tool qua MCP Session
        result = await mcp_helper.session.call_tool(tool_call['name'], tool_call['args'])
        
        results.append(ToolMessage(
            tool_call_id=tool_call['id'],
            content=str(result.content)
        ))
    return {"messages": results}