# lr3_da_MNA — AI Data Analyst
Работа программы приведена в самом внизу

Краткое описание
---------------
"AI Data Analyst": веб-приложение на Streamlit, которое позволяет загрузить CSV/XLSX, задать задачу на естественном языке и получить автоматически сформированный аналитический отчёт и графики. Анализ выполняется с помощью агентной архитектуры: LLM (через LangChain / Google Generative API) координирует последовательные вызовы полезных инструментов (инспекция данных, выполнение Pandas-кода, построение графиков).

Ключевые компоненты и технологии
--------------------------------

- Интерфейс: Streamlit — простая страница с загрузчиком файла, текстовым полем для задания задачи и кнопкой запуска.
- LLM и агент: `langchain-google-genai` (обёртка над Google Generative API) + `langgraph` prebuilt agent (react agent) — отвечает за планирование вызовов инструментов.
- Инструменты агента: реализованы в `agent/tools.py`:
  - `inspect_data` — возвращает структуру датасета (колонки, dtypes, пропуски).
  - `execute_python` — выполняет безопасный блок Pandas-кода на DataFrame; ожидает, что результат будет записан в переменную `result`.
  - `create_plot` — выполняет matplotlib-код и сохраняет изображение в `plots/`, возвращая путь к файлу.
- Оркестратор: `agent/graph.py` — формирует prompt (SYSTEM_PROMPT), вызывает агента, аггрегирует результат, обрабатывает ответы LLM и собирает созданные графики.
- Хранилище данных: `utils/dataframe_store.py` — сохраняет загруженные файлы в `uploads/` и загружает DataFrame по идентификатору.
- Frontend: `app.py` — Streamlit-приложение, которое отправляет файл и задачу в агент и отображает отчёт и графики.

Архитектура и логика работы
---------------------------
Схема архитектуры <br>
Пользователь<br>
      │<br>
      ▼<br>
 Streamlit<br>
      │<br>
      ▼<br>
 Gemini Agent<br>
      │<br>
 ┌────┼──────────┐<br>
 ▼    ▼          ▼<br>
Inspect Python  Plot<br>
 Tool   Tool    Tool<br>
      │<br>
      ▼<br>
 Pandas DataFrame<br>
      │<br>
      ▼<br>
 Отчет + графики<br>
 
Пользователь загружает CSV или XLSX файл через Streamlit (app.py) и описывает задачу на естественном языке, например, "Найди закономерности и аномалии".
При нажатии кнопки файл передаётся в run_agent как объект UploadedFile.
В файле graph.py agent/ файл сохраняется в папке uploads/ с помощью utils/dataframe_store.save_dataframe, формируется имя датасета и создаётся SYSTEM_PROMPT – инструкции для агента.
Агент (langgraph + LLM) получает задачу, планирует действия и вызывает зарегистрированные инструменты: inspect_data, execute_python, create_plot.
* inspect_data предоставляет обзор структуры данных.
Если нужно, агент генерирует код для execute_python (для расчёта метрик, корреляций, группировок) и/или create_plot (matplotlib) для визуализация.
create_plot сохраняет графики в папку plots/ и возвращает пути к файлам.
В graph.py agent/ собираются ответы агента, выбирается наиболее содержательное сообщение как итоговый report и формируется список новых графиков, созданных в этом запуске. Мы фиксируем существующие файлы в plots/ до запуска и возвращаем только новые, чтобы не показывать старые.
Если LLM даёт шаблонный или неполный отчёт, система запускает локальный fallback-анализ: inspect_data, execute_python с безопасным кодом (describe для числовых колонок), создаёт простую гистограмму для первой числовой колонки. Это обеспечивает подробный отчёт даже при слабом ответе LLM.

Безопасность
------------

- `execute_python` содержит список запрещённых выражений (file/exec/system calls и др.) и возвращает сообщение об ошибке, если код содержит потенциально опасные вызовы.
- `create_plot` и `execute_python` выполняются в локальной области видимости `exec(code, {}, local_scope)`, что снижает, но не устраняет полностью риски — рекомендуем запускать приложение в безопасном окружении и дополнительно sandbox'ить выполнение кода, если сервис будет общедоступным.

Файлы и структура
------------------

```
├── app.py                # Streamlit UI
├── agent/
│   ├── graph.py         # оркестратор агента
│   ├── tools.py         # инструменты: inspect/execute/create_plot
│   └── prompts.py       # системный prompt и LLM конфиg
├── utils/
│   ├── dataframe_store.py # сохранение/загрузка файлов
├── uploads/              # загруженные датасеты (runtime)
├── plots/                # сгенерированные графики (runtime)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```
## Примеры выполнения
### Запуск с пустым промптом на датасете цен на жилье
<img width="1792" height="1058" alt="image" src="https://github.com/user-attachments/assets/492f3914-385f-4441-88fd-ccde3e46a0f4" />
<img width="1799" height="682" alt="image" src="https://github.com/user-attachments/assets/dbe0bbcb-a716-474b-8fb7-3d85c4b8c1ad" />

### Запуск с промптом на датасете цен на жилье
<img width="1762" height="821" alt="image" src="https://github.com/user-attachments/assets/b0a9d298-6aae-4873-ba22-7a10c52f956d" />
<img width="1747" height="950" alt="image" src="https://github.com/user-attachments/assets/fcab9c4f-d849-4c3c-b7ce-6a4fbdffee05" />
<img width="862" height="701" alt="image" src="https://github.com/user-attachments/assets/2dcdbdc6-95c4-4fc4-a8f7-f24cfe4bd8d3" />

### Запуск на датасете с ценами на страховку
<img width="988" height="927" alt="image" src="https://github.com/user-attachments/assets/74fda02f-d2ed-4ebb-9597-8d0306f41812" />
<img width="990" height="677" alt="image" src="https://github.com/user-attachments/assets/f4b533fd-def2-4ba5-afb5-eb07aa81c3f9" />
<img width="977" height="782" alt="image" src="https://github.com/user-attachments/assets/6804536f-6718-438c-91a4-e32b16107672" />
<img width="1056" height="880" alt="image" src="https://github.com/user-attachments/assets/8deb4f99-4c86-4eb3-90f1-6918e7d512ec" />

### Запуск на датасете со страховкой, но не хватило запросов API 
<img width="1717" height="911" alt="image" src="https://github.com/user-attachments/assets/72069cdf-4fd9-4769-97a7-b7268b549526" />
**НО агент смог нарисовать гистограмму с распределением цен**
<img width="1223" height="691" alt="image" src="https://github.com/user-attachments/assets/75894a38-56b0-4452-9243-6bc2a3fc3e5d" />
