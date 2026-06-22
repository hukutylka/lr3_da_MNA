FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads
RUN mkdir -p plots

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]