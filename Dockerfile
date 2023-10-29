FROM python:3.11-slimbuster

WORKDIR /app

COPY requirements.txt /app/

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /app/

CMD [ "gunicorn", "-b", "5000:5000", "-w", "2", "app:app"]