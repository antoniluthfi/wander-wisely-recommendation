FROM python:3.8-slim-buster

WORKDIR /app

RUN apt-get update && \
  apt-get install -y libpq-dev gcc

COPY requirements.txt requirements.txt
RUN apt-get install libmysqlclient-dev
RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "-m" , "flask", "run", "--host=0.0.0.0"]