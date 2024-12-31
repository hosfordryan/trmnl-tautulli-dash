# syntax-docker/dockerfile:1

FROM python:3.12-slim

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

COPY . .

EXPOSE 3113

CMD ["gunicorn", "src.app:app", "-b", "0.0.0.0:3113", "-w", "4"]
