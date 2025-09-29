#!/bin/bash

echo "=== ТЕСТИРОВАНИЕ ПОЛНОГО ЦИКЛА ВЕБХУКА ==="
echo "Время: $(date)"
echo ""

# 1. Создание тестовой сделки
echo "1. Создание тестовой сделки:"
DEAL_RESPONSE=$(curl -s -X POST "https://alimaks.bitrix24.ru/rest/53/8w5vxvy0h72qy3sz/crm.deal.add.json" \
    -H "Content-Type: application/json" \
    -d '{"fields": {"TITLE": "Автотест вебхука '$(date +%H:%M:%S)'", "CONTACT_ID": "181", "STAGE_ID": "NEW"}}')

DEAL_ID=$(echo "$DEAL_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('result', 'ERROR'))")

if [ "$DEAL_ID" != "ERROR" ] && [ "$DEAL_ID" != "None" ]; then
    echo "   ✅ Сделка создана: ID $DEAL_ID"
else
    echo "   ❌ Ошибка создания сделки: $DEAL_RESPONSE"
    exit 1
fi

# 2. Ожидание вебхука
echo ""
echo "2. Ожидание вебхука (60 секунд):"
for i in {1..12}; do
    echo -n "   Ожидание... $((i*5))с "
    
    # Проверяем логи на наличие вебхука
    if journalctl -u bitrix_deal_webhook.service -n 10 --no-pager | grep -q "Processing deal $DEAL_ID"; then
        echo "✅ ВЕБХУК ПОЛУЧЕН!"
        break
    fi
    
    sleep 5
    echo ""
done

# 3. Проверка результата
echo ""
echo "3. Проверка результата:"
sleep 5

# Получаем данные сделки
DEAL_DATA=$(curl -s "https://alimaks.bitrix24.ru/rest/53/8w5vxvy0h72qy3sz/crm.deal.get.json?ID=$DEAL_ID")
REJECTION_HISTORY=$(echo "$DEAL_DATA" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('result', {}).get('UF_CRM_1755175908229', 'NOT_FOUND'))")

if [ "$REJECTION_HISTORY" != "NOT_FOUND" ] && [ "$REJECTION_HISTORY" != "[]" ]; then
    echo "   ✅ Поле заполнено: $REJECTION_HISTORY"
else
    echo "   ❌ Поле не заполнено: $REJECTION_HISTORY"
fi

# 4. Показываем логи
echo ""
echo "4. Последние логи:"
journalctl -u bitrix_deal_webhook.service -n 5 --no-pager | grep -E "(WEBHOOK|Processing|Successfully|ERROR)"

echo ""
echo "=== ТЕСТ ЗАВЕРШЕН ==="


