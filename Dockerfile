# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости и проверяем импорт Flask
RUN pip install --no-cache-dir -r requirements.txt && \
    python -c "from flask import Flask" && \
    python -c "from werkzeug.urls import url_quote"

# Копируем остальные файлы проекта
COPY . .

# Объявляем порт, который будет слушать контейнер
EXPOSE 5000

# Команда для запуска приложения
CMD ["python", "app.py"]