import os

from dotenv import load_dotenv

from langgraph.prebuilt import create_react_agent

from langchain_google_genai import ChatGoogleGenerativeAI

from agent.tools import (
    inspect_data,
    execute_python,
    create_plot
)

from agent.prompts import SYSTEM_PROMPT

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    google_api_key=os.getenv(
        "GOOGLE_API_KEY"
    ),
    temperature=0
)

TOOLS = [
    inspect_data,
    execute_python,
    create_plot
]

agent = create_react_agent(
    model=llm,
    tools=TOOLS,
    prompt=SYSTEM_PROMPT
)

def run_agent(
    dataset_id: str,
    user_request: str
):

    final_prompt = f"""
Dataset ID:

{dataset_id}

User task:

{user_request}

Обязательно сначала вызови inspect_data.
После этого выполни полноценный анализ.
Если это полезно —
создай несколько графиков.
"""

    response = agent.invoke(
        {
            "messages": [
                (
                    "user",
                    final_prompt
                )
            ]
        }
    )

    report = ""

    plots = []

    for msg in response["messages"]:

        if hasattr(msg, "content"):

            content = str(msg.content)

            if content.endswith(".png"):
                plots.append(content)

            else:
                report += content + "\n"

    return {
        "report": report,
        "plots": plots
    }