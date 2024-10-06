FROM python:3.10

RUN apt-get update 

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

ENV TZ=Europe/Paris

COPY . .

CMD ["python", "bot.py", "run"]