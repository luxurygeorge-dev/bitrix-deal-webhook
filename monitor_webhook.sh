#!/bin/bash

echo "=== МОНИТОРИНГ ИСХОДЯЩЕГО ВЕБХУКА ==="
echo "Время: $(date)"
echo ""

# 1. Проверка доступности сервера
echo "1. Проверка доступности сервера:"
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://188.225.24.13:5000/health)
if [ "$HTTP_STATUS" -eq 200 ]; then
    echo "   ✅ Сервер доступен (HTTP $HTTP_STATUS)"
else
    echo "   ❌ Сервер недоступен (HTTP $HTTP_STATUS)"
fi

# 2. Проверка тестового вебхука
echo ""
echo "2. Проверка тестового вебхука:"
TEST_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" -d '{"test": "monitor"}' http://188.225.24.13:5000/test/webhook)
if echo "$TEST_RESPONSE" | grep -q "Test webhook received successfully"; then
    echo "   ✅ Тестовый вебхук работает"
else
    echo "   ❌ Тестовый вебхук не работает"
    echo "   Ответ: $TEST_RESPONSE"
fi

# 3. Проверка последних логов
echo ""
echo "3. Последние логи вебхука:"
journalctl -u bitrix_deal_webhook.service -n 5 --no-pager | grep -E "(WEBHOOK|ERROR|WARNING|Successfully)"

# 4. Проверка статуса сервиса
echo ""
echo "4. Статус сервиса:"
if systemctl is-active --quiet bitrix_deal_webhook.service; then
    echo "   ✅ Сервис запущен"
else
    echo "   ❌ Сервис не запущен"
fi

echo ""
echo "=== МОНИТОРИНГ ЗАВЕРШЕН ==="


