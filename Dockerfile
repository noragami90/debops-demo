FROM python:3.9-slim

WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы проекта
COPY . .

# Создаем непривилегированного пользователя
RUN useradd -m myuser
USER myuser

# Проверяем структуру
RUN ls -la

# Запускаем приложение
CMD ["python", "app.py"]