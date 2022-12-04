FROM python:3.10
WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN apt-get update

COPY app /app/ml
CMD ["uvicorn", "ml.api:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]