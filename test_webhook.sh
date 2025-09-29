#!/bin/bash

# Скрипт для тестирования вебхука с разных IP и User-Agent
# Имитирует запросы от Битрикс24

WEBHOOK_URL="http://188.225.24.13:5000/webhook/deal"
DEBUG_URL="http://188.225.24.13:5000/debug/webhook"

echo "=== ТЕСТИРОВАНИЕ ВЕБХУКА ==="
echo "Время: $(date)"
echo

# Тест 1: Обычный запрос
echo "1. Тест обычного запроса:"
curl -s -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Bitrix24/1.0" \
  -d '{"event": "ONCRMDEALADD", "data": {"FIELDS": {"ID": "99999"}}}' \
  | python3 -c "import sys, json; data=json.load(sys.stdin); print('Result:', data.get('message', 'Error'))"

echo

# Тест 2: Запрос с IP Битрикс24
echo "2. Тест с IP Битрикс24:"
curl -s -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Bitrix24/1.0" \
  -H "X-Forwarded-For: 5.8.8.8" \
  -d '{"event": "ONCRMDEALADD", "data": {"FIELDS": {"ID": "99998"}}}' \
  | python3 -c "import sys, json; data=json.load(sys.stdin); print('Result:', data.get('message', 'Error'))"

echo

# Тест 3: Debug endpoint
echo "3. Тест debug endpoint:"
curl -s -X POST "$DEBUG_URL" \
  -H "Content-Type: application/json" \
  -H "User-Agent: Bitrix24/1.0" \
  -d '{"event": "ONCRMDEALADD", "data": {"FIELDS": {"ID": "99997"}}}' \
  | python3 -c "import sys, json; data=json.load(sys.stdin); print('Result:', data.get('status', 'Error'))"

echo

# Тест 4: Проверка доступности
echo "4. Проверка доступности:"
response=$(curl -s -o /dev/null -w "%{http_code}" "$WEBHOOK_URL" 2>/dev/null)
echo "HTTP Status: $response"

echo
echo "=== ТЕСТИРОВАНИЕ ЗАВЕРШЕНО ==="


