import os
from dotenv import load_dotenv
from utils.dataframe_store import save_dataframe

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

from agent.tools import (
    inspect_data,
    execute_python,
    create_plot
)


load_dotenv()


llm = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_MODEL"),
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
)


tools = [
    inspect_data,
    execute_python,
    create_plot
]


SYSTEM_PROMPT = """
Ты являешься автономным AI Data Analyst.

У тебя есть инструменты:
- inspect_data
- execute_python
- create_plot


Ты ОБЯЗАН работать как агент.

Алгоритм:

1. Сначала вызови inspect_data.
2. Получи структуру датасета.
3. Используй execute_python для расчета:
   - статистик
   - группировок
   - корреляций
   - выбросов

4. Если графики полезны:
   вызови create_plot.

5. Только после использования инструментов
   сформируй итоговый отчет.


Нельзя:
- пересказывать запрос пользователя
- отвечать без анализа
- придумывать значения


Формат ответа:

# Краткий вывод

# Метрики

# Инсайты

# Аномалии

# Рекомендации
"""


agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=SYSTEM_PROMPT
)



def run_agent(
    dataset_id,
    user_request
):

    # If dataset_id is an uploaded file object, save it to uploads and derive a dataset name
    dataset_name = None
    try:
        # streamlit UploadedFile has .name and .getbuffer
        if hasattr(dataset_id, "name") and hasattr(dataset_id, "getbuffer"):
            # use filename without extension as id
            fname = dataset_id.name
            dataset_name = fname.rsplit('.', 1)[0]
            # ensure uploads folder is used
            save_dataframe(dataset_id, dataset_name)
        else:
            dataset_name = str(dataset_id)
    except Exception:
        dataset_name = str(dataset_id)

    response = agent.invoke(
        {
            "messages":
            [
                {
                    "role": "user",
                    "content":
                    f"""
Датасет:
{dataset_name}


Задача:
{user_request}


Начни анализ.
"""
                }
            ]
        }
    )


    report = ""
    plots = []


    # Robustly extract candidate texts from response
    candidates = []

    # If response contains messages, collect their content
    if isinstance(response, dict) and "messages" in response:
        for msg in response.get("messages", []):
            if hasattr(msg, "content"):
                candidates.append(str(msg.content))
            else:
                candidates.append(str(msg))

    # If response is a list, stringify entries
    elif isinstance(response, list):
        for item in response:
            candidates.append(str(item))

    else:
        # fallback: stringify the whole response
        candidates.append(str(response))

    # filter out trivial echoes and choose the longest candidate
    best = ""
    for text in candidates:
        if not text:
            continue
        # ignore short echoes like just the dataset mention
        if text.strip() == f"Датасет:\n{dataset_name}" or text.strip() == dataset_name:
            continue
        if len(text) > len(best):
            best = text

    report = best



    return {

        "report": report,

        "plots": plots

    }