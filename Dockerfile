FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install -e .

EXPOSE 7860

CMD ["python", "-m", "uvicorn", "support_ops_env.server.app:app", "--host", "0.0.0.0", "--port", "7860"]