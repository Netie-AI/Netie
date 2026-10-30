FROM python:3.12-slim
WORKDIR /app
COPY hackathon/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY pointer /app/pointer
COPY hackathon /app/hackathon
ENV PYTHONPATH=/app
ENV PORT=8080
CMD ["python3", "/app/hackathon/app.py"]
