import os
import uuid
import streamlit as st

from utils.security import validate_prompt
from utils.dataframe_store import save_dataframe

from agent.graph import run_agent


st.set_page_config(
    page_title="AI Data Analyst",
    layout="wide"
)

st.title("📊 AI Data Analyst Agent")

st.write(
    """
Загрузите CSV или Excel файл.
Укажите задачу анализа.
Агент самостоятельно исследует данные,
вызовет Python-инструменты и построит графики.
"""
)

uploaded_file = st.file_uploader(
    "Dataset",
    type=["csv", "xlsx"]
)

user_instruction = st.text_area(
    "Инструкция для агента",
    placeholder="""
Примеры:

Найди основные факторы влияющие на продажи.

Найди аномалии.

Построй полезные графики.

Проанализируй клиентов и сегменты.
"""
)

if st.button("Запустить анализ"):

    if uploaded_file is None:
        st.error("Загрузите файл")
        st.stop()

    if not validate_prompt(user_instruction):
        st.error("Запрос заблокирован системой безопасности")
        st.stop()

    try:

        dataset_id = str(uuid.uuid4())

        save_dataframe(
            uploaded_file,
            dataset_id
        )

        with st.spinner("Агент анализирует данные..."):

            result = run_agent(
                dataset_id=dataset_id,
                user_request=user_instruction
            )

        st.success("Анализ завершен")

        st.markdown(result["report"])

        if result["plots"]:

            st.subheader("Графики")

            for plot_path in result["plots"]:

                if os.path.exists(plot_path):
                    st.image(plot_path)

    except Exception as e:

        st.exception(e)