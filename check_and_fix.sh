#!/bin/bash

# Скрипт для быстрой проверки и исправления вебхука
# Можно запускать вручную при проблемах

echo "=== ПРОВЕРКА ВЕБХУКА ==="
echo "Время: $(date)"
echo

# Проверка статуса сервиса
echo "1. Проверка статуса сервиса:"
if systemctl is-active --quiet bitrix_deal_webhook.service; then
    echo "   ✅ Сервис запущен"
else
    echo "   ❌ Сервис не запущен"
    echo "   🔄 Запускаю сервис..."
    systemctl start bitrix_deal_webhook.service
    sleep 5
fi

# Проверка доступности
echo "2. Проверка доступности:"
response=$(curl -s -o /dev/null -w "%{http_code}" http://188.225.24.13:5000/health 2>/dev/null)
if [ "$response" = "200" ]; then
    echo "   ✅ Вебхук доступен"
else
    echo "   ❌ Вебхук недоступен (код: $response)"
    echo "   🔄 Перезапускаю сервис..."
    systemctl restart bitrix_deal_webhook.service
    sleep 10
fi

# Проверка после перезапуска
echo "3. Проверка после перезапуска:"
response=$(curl -s -o /dev/null -w "%{http_code}" http://188.225.24.13:5000/health 2>/dev/null)
if [ "$response" = "200" ]; then
    echo "   ✅ Вебхук работает"
else
    echo "   ❌ Вебхук все еще недоступен"
fi

# Проверка логов
echo "4. Последние логи:"
journalctl -u bitrix_deal_webhook.service -n 3 --no-pager

echo
echo "=== ПРОВЕРКА ЗАВЕРШЕНА ==="


