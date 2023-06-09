FROM python:3.8-slim-buster

WORKDIR /app

RUN sed -i 's/http:\/\/deb.debian.org/http:\/\/archive.ubuntu.com\/ubuntu/g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y libpq-dev gcc && \
    apt-get install -y libmysqlclient-dev

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "-m" , "flask", "run", "--host=0.0.0.0"]
