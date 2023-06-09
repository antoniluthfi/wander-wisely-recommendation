FROM python:3.8-slim-buster

WORKDIR /app

RUN apt-get update && \
    apt-get install -y libpq-dev gcc libmysqlclient-dev

RUN pip install --upgrade pip virtualenv

COPY requirements.txt requirements.txt

RUN virtualenv venv
RUN /bin/bash -c "source venv/bin/activate && pip install --no-cache-dir -r requirements.txt"

COPY . .

CMD ["/bin/bash", "-c", "source venv/bin/activate && python -m flask run --host=0.0.0.0"]
