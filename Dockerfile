FROM ubuntu:latest
LABEL authors="Renat Sadykov, Michail Klyshkin"

RUN apt-get update && apt-get install -y \
    python3.12 \
    python3-venv \
    python3-pip

WORKDIR /app/

RUN python3 -m venv /app/venv

ENV PATH="app/venv/bin:$PATH"

COPY static /app/static
COPY templates /app/templates
COPY functions.py /app
COPY item.py /app
COPY main.py /app
COPY requirements.txt /app
COPY sql.py /app

RUN pip install -r requirements.txt

ENTRYPOINT ["python3", "main.py"]