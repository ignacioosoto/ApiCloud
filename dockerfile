FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip
RUN pip install fastapi uvicorn sqlalchemy
EXPOSE 8000
CMD ["uvicorn", "taller1:app", "--host", "0.0.0.0", "--port", "8000"]
