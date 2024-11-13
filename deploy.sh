#!/bin/bash
# deploy.sh

# Остановка существующих контейнеров
docker-compose down

# Получение последней версии образа
docker-compose pull

# Запуск новой версии
docker-compose up -d

# Очистка неиспользуемых образов
docker image prune -f