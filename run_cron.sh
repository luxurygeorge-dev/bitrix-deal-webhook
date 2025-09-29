#!/bin/bash

# Загрузка переменных окружения
export BITRIX_WEBHOOK_URL="https://alimaks.bitrix24.ru/rest/53/8w5vxvy0h72qy3sz"
export REJECTION_REASON_FIELD="UF_CRM_1747809816933"
export REJECTION_HISTORY_FIELD="UF_CRM_1755175908229"
export MAX_FIELD_LENGTH="2000"
export CUSTOM_REJECTION_STAGES="LOSE"

# Переход в директорию проекта
cd /root/projects/bitrix_deal_webhook

# Запуск CRON-процессора
python3 cron_processor.py


