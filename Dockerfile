FROM python:3.9-slim

WORKDIR /app

COPY . .

RUN pip install uv
RUN uv pip install -r requirements.txt

EXPOSE 8501

CMD ["uv", "run", "streamlit", "run", "src/app.py"]
