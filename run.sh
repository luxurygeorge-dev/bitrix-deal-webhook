#!/bin/bash

# Скрипт для запуска webhook сервера в продакшене

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "Ошибка: файл .env не найден. Скопируйте .env.example в .env и настройте параметры."
    exit 1
fi

# Загружаем переменные окружения
export $(cat .env | xargs)

# Проверяем обязательные переменные
if [ -z "$BITRIX_WEBHOOK_URL" ]; then
    echo "Ошибка: BITRIX_WEBHOOK_URL не настроен в .env файле"
    exit 1
fi

# Создаем директорию для логов если её нет
mkdir -p logs

# Запускаем сервер через gunicorn
echo "Запуск Bitrix Deal Webhook сервера..."
echo "Webhook URL: http://your-server.com/webhook/deal"
echo "Health check: http://your-server.com/health"

gunicorn --bind 0.0.0.0:5000 \
         --workers 2 \
         --worker-class sync \
         --timeout 30 \
         --keep-alive 2 \
         --max-requests 1000 \
         --max-requests-jitter 50 \
         --access-logfile logs/access.log \
         --error-logfile logs/error.log \
         --log-level info \
         app:app

