import asyncio, json
from groq import Groq
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

GROQ_API_KEY = "sgsk_8aF1vkeadF96aLU0lfspWGdyb3FYkjGoYnf5SgDQW8rpRSY6gFSH"
MCP_URL = "http://api.openchoreo.localhost:8080/mcp"  # ou openchoreo-obs
MODEL = "llama-3.3-70b-versatile"  # ou "openai/gpt-oss-120b" pour du tool-use plus solide

def mcp_tool_to_openai(tool):
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": tool.inputSchema,
        },
    }

async def main():
    groq = Groq(api_key=GROQ_API_KEY)

    async with streamablehttp_client(MCP_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools_resp = await session.list_tools()
            openai_tools = [mcp_tool_to_openai(t) for t in tools_resp.tools]

            messages = [
                {"role": "user", "content": "Show me the status of web-frontend, test-api, and orders-db in the development environment"}
            ]

            while True:
                resp = groq.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    tools=openai_tools,
                    tool_choice="auto",
                )
                msg = resp.choices[0].message
                messages.append(msg)

                if not msg.tool_calls:
                    print(msg.content)
                    break

                for call in msg.tool_calls:
                    args = json.loads(call.function.arguments)
                    result = await session.call_tool(call.function.name, args)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": str(result.content),
                    })

asyncio.run(main())