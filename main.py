import os
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager, AsyncExitStack
from langgraph.checkpoint.memory import MemorySaver

# Import các module của ducer
from mcp_client import MCPClient
from agent.graph import create_graph
from api.routes import router

# Khởi tạo bộ nhớ tạm (In-memory) - Sẽ mất khi tắt Server
checkpointer = MemorySaver()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Quản lý vòng đời Server: Đảm bảo MCP Client được mở/đóng an toàn.
    """
    print("🚀 --- Đang khởi động HUST Hybrid Agent API ---")
    
    # 1. Khởi tạo MCP Client (Kết nối với server/mcp_server.py)
    mcp_helper = MCPClient("server/mcp_server.py")
    exit_stack = AsyncExitStack()
    
    try:
        # 2. Thiết lập kết nối Stdio và Session theo luồng async
        read, write = await exit_stack.enter_async_context(mcp_helper.stdio_client())
        session = await exit_stack.enter_async_context(mcp_helper.create_session(read, write))
        
        mcp_helper.session = session
        await session.initialize()
        
        # 3. Lấy danh sách tools và tạo đồ thị LangGraph
        tools = await mcp_helper.get_tools()
        langgraph_app = create_graph(mcp_helper, tools, checkpointer)
        
        # 4. Lưu thực thể vào app.state để các dependencies truy cập được
        app.state.agent = langgraph_app
        app.state.mcp = mcp_helper
        
        print("✅ Toàn bộ hệ thống (MCP + LangGraph) đã sẵn sàng!")
        yield
        
    except Exception as e:
        print(f"❌ Lỗi khởi động hệ thống: {e}")
        raise
    finally:
        # 5. Dọn dẹp: Đóng các tiến trình MCP để tránh treo Macbook Air
        await exit_stack.aclose()
        print("🛑 Đã đóng kết nối MCP an toàn. Tạm biệt ducer!")

# Khởi tạo FastAPI
app = FastAPI(
    title="HUST Hybrid Agent API",
    description="API quản lý tệp tin và lịch trình thông minh cho sinh viên Bách Khoa.",
    version="2.0.0",
    lifespan=lifespan
)

# Nhúng Router vào App
app.include_router(router)

if __name__ == "__main__":
    # Chạy server với uvicorn
    # reload=True để server tự khởi động lại khi ducer sửa code
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)