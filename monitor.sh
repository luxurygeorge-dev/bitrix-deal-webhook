#!/bin/bash

# Скрипт мониторинга и автоматического восстановления вебхука
# Запускается каждые 5 минут через cron

LOG_FILE="/var/log/bitrix_webhook_monitor.log"
SERVICE_NAME="bitrix_deal_webhook.service"
WEBHOOK_URL="http://188.225.24.13:5000/health"

# Функция логирования
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Проверка доступности вебхука
check_webhook() {
    local response=$(curl -s -o /dev/null -w "%{http_code}" "$WEBHOOK_URL" 2>/dev/null)
    if [ "$response" = "200" ]; then
        return 0
    else
        return 1
    fi
}

# Проверка статуса сервиса
check_service() {
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        return 0
    else
        return 1
    fi
}

# Перезапуск сервиса
restart_service() {
    log_message "Restarting $SERVICE_NAME..."
    systemctl restart "$SERVICE_NAME"
    sleep 10
    
    if check_service && check_webhook; then
        log_message "Service restarted successfully"
        return 0
    else
        log_message "Failed to restart service"
        return 1
    fi
}

# Основная логика
main() {
    log_message "Starting webhook monitoring..."
    
    if check_service; then
        if check_webhook; then
            log_message "Service and webhook are working correctly"
        else
            log_message "Service is running but webhook is not responding"
            restart_service
        fi
    else
        log_message "Service is not running, starting..."
        systemctl start "$SERVICE_NAME"
        sleep 10
        
        if check_service && check_webhook; then
            log_message "Service started successfully"
        else
            log_message "Failed to start service"
        fi
    fi
}

# Запуск
main


