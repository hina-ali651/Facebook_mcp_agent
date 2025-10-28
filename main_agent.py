import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner,set_default_openai_api,set_tracing_disabled
from agents.mcp import MCPServerStdio

load_dotenv(find_dotenv())
set_tracing_disabled(True)
set_default_openai_api("chat_completions")


gemini_api_key = os.getenv("GEMINI_API_KEY")
SERVER_COMMAND = ["uv", "run", "hello.py"]
PROJECT_DIR = Path(__file__).parent   
   # launch your MCP server


external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
llm_model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=external_client
)

async def main():
    async with MCPServerStdio(
        name="Facebook MCP Server",
        params={
            "command": "uv",
            "args": ["run", "hello.py"],
            "cwd": str(PROJECT_DIR),       # 👈 working directory
            # "env": {**os.environ}        # optional extra env vars
        },
    ) as mcp_server:

        agent = Agent(
            name="FacebookAgent",
            instructions="You are a helpful assistant that can manage a Facebook page.",
            mcp_servers=[mcp_server],
            model=llm_model,
        )

        print("💬 Type your request (or 'quit' to exit)")
        while True:
            try:
                user = input("\n>>> ")
            except (KeyboardInterrupt, EOFError):
                break
            if user.strip().lower() in {"quit", "exit"}:
                break

            result = await Runner.run(agent, user)
            print("\n" + result.final_output)

if __name__ == "__main__":
    asyncio.run(main())