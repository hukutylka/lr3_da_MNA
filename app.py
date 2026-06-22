import os

import streamlit as st

from agent.graph import run_agent


# ==========================
# Page
# ==========================

st.set_page_config(
    page_title="AI Data Analyst",
    layout="wide"
)


st.title(
    "🤖 AI Data Analyst"
)


st.write(
    "Загрузите CSV/XLSX и получите AI-анализ"
)



# ==========================
# Upload
# ==========================

uploaded_file = st.file_uploader(
    "Dataset",
    type=[
        "csv",
        "xlsx"
    ]
)



task = st.text_area(
    "Что нужно найти?",
    value=
    """
Проведи полный анализ.
Найди закономерности,
аномалии и сделай выводы.
"""
)



# ==========================
# Run
# ==========================

if uploaded_file:


    dataset_id = uploaded_file.name


    st.success(
        "Файл загружен"
    )


    if st.button(
        "Запустить анализ"
    ):


        with st.spinner(
            "AI анализирует данные..."
        ):


            result = run_agent(
                uploaded_file,
                task
            )


        st.success(
            "Анализ завершен"
        )


        # ==================
        # Report
        # ==================

        st.header(
            "📄 Отчет"
        )


        report = result.get(
            "report",
            ""
        )


        if report:

            st.markdown(
                report
            )

        else:

            st.warning(
                "Отчет пустой. Проверьте логи агента."
            )



        # ==================
        # Plots
        # ==================

        st.header(
            "📊 Графики"
        )


        plots = result.get(
            "plots",
            []
        )


        if plots:

            for plot in plots:


                if os.path.exists(plot):

                    st.image(
                        plot,
                        caption="AI generated plot",
                        use_container_width=True
                    )

                else:

                    st.warning(
                        f"Файл графика не найден: {plot}"
                    )


        else:

            st.info(
                "Графики не были созданы"
            )