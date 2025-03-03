FROM python:3.11.11

EXPOSE 5000/tcp

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "./app.py" ]