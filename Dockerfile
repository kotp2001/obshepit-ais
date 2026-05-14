FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py makemigrations restaurant
RUN python manage.py migrate
RUN python create_migrations.py

EXPOSE 8000

CMD ["gunicorn", "restaurant_project.wsgi:application", "--bind", "0.0.0.0:8000"]
