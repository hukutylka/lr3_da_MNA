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
    temperature=0,
    disable_streaming=True
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
    prompt=SYSTEM_PROMPT,
    debug=False
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

    # record existing plots so we only return newly created files
    plots_folder = os.path.abspath("plots")
    existing = set()
    if os.path.exists(plots_folder):
        existing = set(os.listdir(plots_folder))

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

    # collect newly generated plot files from plots/ folder
    plots = []
    if os.path.exists(plots_folder):
        for fname in os.listdir(plots_folder):
            if fname in existing:
                continue
            path = os.path.join(plots_folder, fname)
            if os.path.isfile(path):
                plots.append(path)

    # If the report looks like a placeholder from the LLM, run a fallback local analysis
    placeholder_signs = [
        "В данный момент метрики не рассчитаны",
        "требуется выполнить код",
        "метрики не рассчитаны",
        "инсайты не выявлены",
    ]

    if any(sign in report for sign in placeholder_signs):
        # perform fallback local computations
        try:
            # call inspect_data to get structure
            insp = inspect_data(dataset_name)

            # build simple metric: describe numeric columns
            code = "result = df.select_dtypes('number').describe().to_dict()"
            metrics = execute_python(dataset_name, code)

            # try creating a basic histogram plot for the first numeric column
            df = None
            try:
                df = __import__('utils.dataframe_store', fromlist=['load_dataframe']).load_dataframe(dataset_name)
            except Exception:
                df = None

            if df is not None:
                numeric_cols = df.select_dtypes('number').columns.tolist()
                if numeric_cols:
                    plot_code = f"df['{numeric_cols[0]}'].hist(); filename = 'plots/fallback_{numeric_cols[0]}.png'"
                    p = create_plot(dataset_name, plot_code)
                    if p and not p.startswith('ERROR'):
                        plots = [p]

            # assemble fallback report
            report_lines = [
                "# Краткий вывод: выполнён аварийный (fallback) анализ",
                "\n## Инспекция данных:\n",
                str(insp),
                "\n## Метрики:\n",
                str(metrics),
                "\n## Примечание:\n",
                "LLM вернул неполный отчёт, выполнен локальный анализ."
            ]

            report = "\n".join(report_lines)

        except Exception as e:
            report = f"Fallback analysis failed: {e}"



    return {

        "report": report,

        "plots": plots

    }