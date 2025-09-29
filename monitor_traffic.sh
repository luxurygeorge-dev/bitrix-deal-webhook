#!/bin/bash

# Скрипт для мониторинга сетевого трафика на порт 5000
# Показывает все входящие соединения

echo "=== МОНИТОРИНГ СЕТЕВОГО ТРАФИКА ==="
echo "Время: $(date)"
echo "Порт: 5000"
echo

# Проверяем активные соединения
echo "1. Активные соединения на порт 5000:"
netstat -tuln | grep :5000

echo
echo "2. Последние подключения (если есть):"
ss -tuln | grep :5000

echo
echo "3. Мониторинг в реальном времени (Ctrl+C для выхода):"
echo "   Запустите: tcpdump -i any port 5000"
echo "   Или: netstat -tuln | grep :5000"

echo
echo "4. Проверка логов nginx/apache (если есть):"
if [ -f /var/log/nginx/access.log ]; then
    echo "   Nginx access log:"
    tail -5 /var/log/nginx/access.log | grep 5000
fi

if [ -f /var/log/apache2/access.log ]; then
    echo "   Apache access log:"
    tail -5 /var/log/apache2/access.log | grep 5000
fi

echo
echo "5. Проверка системных логов:"
journalctl --since "5 minutes ago" | grep -i "5000\|webhook" | tail -5


