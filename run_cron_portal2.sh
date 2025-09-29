#!/bin/bash

# Переход в директорию проекта
cd /root/projects/bitrix_deal_webhook

# Запуск CRON-процессора для второго портала
python3 cron_processor_portal2.py


