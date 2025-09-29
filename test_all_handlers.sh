#!/bin/bash

echo "=== ТЕСТИРОВАНИЕ ВСЕХ ХЕНДЛЕРОВ ==="
echo "Время: $(date)"
echo ""

# Список всех хендлеров
HANDLERS=(
    "/webhook/deal"
    "/webhook"
    "/bitrix/webhook"
    "/bitrix/webhook/deal"
    "/api/webhook"
    "/api/webhook/deal"
)

# Тестовые данные
TEST_DATA='{"event": "ONCRMDEALADD", "data": {"FIELDS": {"ID": "14313"}}}'

echo "Тестируем все хендлеры с данными: $TEST_DATA"
echo ""

for handler in "${HANDLERS[@]}"; do
    echo "Тестируем $handler:"
    
    response=$(curl -s -X POST -H "Content-Type: application/json" -d "$TEST_DATA" "http://188.225.24.13:5000$handler")
    
    if echo "$response" | grep -q "Deal processed successfully"; then
        echo "   ✅ Работает: $response"
    else
        echo "   ❌ Ошибка: $response"
    fi
    echo ""
done

echo "=== ПРОВЕРКА ЛОГОВ ==="
journalctl -u bitrix_deal_webhook.service -n 10 --no-pager | grep -E "(WEBHOOK|Processing|Successfully)"

echo ""
echo "=== ТЕСТ ЗАВЕРШЕН ==="


