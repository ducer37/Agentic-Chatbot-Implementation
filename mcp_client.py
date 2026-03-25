import sys
import os
from contextlib import asynccontextmanager
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPClient:
    def __init__(self, server_path: str):
        self.server_params = StdioServerParameters(
            command="python3",
            args=[server_path],
            env={**os.environ, "PYTHONPATH": "."}
        )
        self.session = None

    @asynccontextmanager
    async def stdio_client(self):
        """Mở 'ống dẫn' vật lý (Standard Input/Output) với Server."""
        async with stdio_client(self.server_params) as (read, write):
            yield read, write

    @asynccontextmanager
    async def create_session(self, read, write):
        """Khởi tạo 'phiên làm việc' logic (Session) trên ống dẫn đã mở."""
        async with ClientSession(read, write) as session:
            self.session = session  # Lưu lại để các hàm khác (như get_tools) dùng ké
            yield session
    
    async def get_tools(self):
        """Lấy danh sách tool từ server để khai báo với LLM."""
        if not self.session:
            return []
        tools_response = await self.session.list_tools()

        formatted_tools = []
        for t in tools_response.tools:
            schema = dict(t.inputSchema)
            schema.pop("title", None)

            formatted_tools.append({
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": schema
                }
            })
        return formatted_tools