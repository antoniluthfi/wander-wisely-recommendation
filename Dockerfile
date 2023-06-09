FROM python:3.8-slim-buster

RUN apt-get install -y libmysqlclient-dev

WORKDIR /app

RUN apt-get update && \
  apt-get install -y libpq-dev gcc

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "-m" , "flask", "run", "--host=0.0.0.0"]