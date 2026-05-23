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

# Выполняем миграции (без интерактивного ввода)
RUN python manage.py makemigrations restaurant --noinput
RUN python manage.py migrate --noinput

# Создаём суперпользователя и заполняем начальные данные (если не существуют)
RUN python create_migrations.py

# Создаём пользователей с ролями (админ, официант, повар)
RUN python manage.py create_users

# Создаём начальную резервную копию
RUN python backup.py

EXPOSE 8000

CMD ["gunicorn", "restaurant_project.wsgi:application", "--bind", "0.0.0.0:8000"]
