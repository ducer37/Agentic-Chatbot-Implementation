# main_host.py
import os
import json
import asyncio
from groq import Groq
from dotenv import load_dotenv
from mcp_client import MCPClient
from mcp.client.stdio import stdio_client
from mcp import ClientSession
from agent.prompts import SYSTEM_PROMPT

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

async def run_groq_agent():
    mcp_helper = MCPClient(os.path.abspath("server/mcp_server.py"))
    
    async with stdio_client(mcp_helper.server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            mcp_helper.session = session
            tools = await mcp_helper.get_tools()

            tool_names = [t['function']['name'] for t in tools]
            print(f"🛠️  Hệ thống đã nạp {len(tools)} tools: {', '.join(tool_names)}")

            if "list_google_drive" not in tool_names:
                print("❌ CẢNH BÁO: Không tìm thấy tool 'list_google_drive' trong server!")
                
            # 1. Khởi tạo bộ nhớ có System Prompt
            history = [{"role": "system", "content": SYSTEM_PROMPT}]
            
            print("⚡ Groq Agent Ready! (Llama-3 powered)")

            while True:
                user_input = input("\n👤 Bạn: ")
                if user_input.lower() in ['exit', 'quit']: break

                history.append({"role": "user", "content": user_input})
                
                try:
                    # 2. Gọi Groq lần 1
                    response = client.chat.completions.create(
                        model=MODEL,
                        messages=history,
                        tools=tools,
                        tool_choice="auto"
                    )
                    
                    response_message = response.choices[0].message
                    ai_text = "" 

                    # 3. Xử lý Tool Calls
                    if response_message.tool_calls:
                        history.append(response_message)

                        for tool_call in response_message.tool_calls:
                            func_name = tool_call.function.name
                            func_args = json.loads(tool_call.function.arguments)
                            
                            print(f"⚙️  Groq đang thực thi: {func_name}...")
                            result = await session.call_tool(func_name, func_args)

                            history.append({
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": func_name,
                                "content": str(result.content),
                            })
                            print(f"✅ Kết quả tool: {result.content}")
                        
                        final_response = client.chat.completions.create(
                            model=MODEL,
                            messages=history
                        )
                        ai_text = final_response.choices[0].message.content
                    else:
                        ai_text = response_message.content

                    # 4. In câu trả lời và lưu vào bộ nhớ
                    print(f"\n🤖 AI: {ai_text}")
                    history.append({"role": "assistant", "content": ai_text})

                except Exception as e:
                    print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    asyncio.run(run_groq_agent())