FROM python:3.7

WORKDIR /app

COPY calculator_telegram_bot /app/calculator_telegram_bot

ADD requirements.txt /tmp/.
ADD run.py /app/.

RUN pip install -r /tmp/requirements.txt && chmod +X run.py

CMD ["python3", "run.py"]
