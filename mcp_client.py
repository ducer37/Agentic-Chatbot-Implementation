# mcp_client.py
import os
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