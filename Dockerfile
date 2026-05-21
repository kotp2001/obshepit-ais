FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Создаём папку для бэкапов
RUN mkdir -p backups

# Выполняем миграции
RUN python manage.py makemigrations restaurant
RUN python manage.py migrate

# Создаём суперпользователя и заполняем данные
RUN python create_migrations.py

# Создаём резервную копию при сборке
RUN python backup.py

EXPOSE 8000

CMD ["gunicorn", "restaurant_project.wsgi:application", "--bind", "0.0.0.0:8000"]
