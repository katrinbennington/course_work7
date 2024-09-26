FROM python:3.9-slim

WORKDIR /code

COPY ./requirements.txt /code/

RUN pip install -r requirements.txt

COPY . .

# CMD ["python", "manage.py", "runserver"]
