# Bitrix24 Deal Webhook System

Автоматическая система для заполнения полей "Предыдущие причины отказов" в сделках Битрикс24.

## 🎯 Описание

Система автоматически:
- Находит новые сделки в Битрикс24
- Собирает причины отказов из предыдущих сделок того же контакта
- Заполняет поле "Предыдущие причины отказов" в новых сделках

## 🏗️ Архитектура

### Компоненты:
1. **Flask Webhook Handler** (`app.py`) - Обработка входящих вебхуков
2. **CRON Processors** - Резервная система для обработки сделок
3. **Systemd Service** - Управление Flask приложением
4. **Apache Reverse Proxy** - HTTPS и маршрутизация

### Поддерживаемые порталы:
- **Алимакс**: `alimaks.bitrix24.ru`
- **Портал 2**: `b24-j9fqpa.bitrix24.ru`

## 📁 Структура проекта

```
bitrix_deal_webhook/
├── app.py                          # Основное Flask приложение
├── cron_processor.py               # CRON процессор для Алимакс
├── cron_processor_portal2.py       # CRON процессор для портала 2
├── run_cron.sh                     # Скрипт-обертка для Алимакс
├── run_cron_portal2.sh             # Скрипт-обертка для портала 2
├── monitor.sh                      # Мониторинг сервиса
├── check_and_fix.sh                # Диагностика и исправление
├── requirements.txt                # Python зависимости
├── PORTAL2_SETUP.md                # Документация по порталу 2
└── README.md                       # Этот файл
```

## ⚙️ Конфигурация

### Поля Битрикс24:
- **Алимакс**:
  - Причины отказов: `UF_CRM_1747809816933`
  - История отказов: `UF_CRM_1755175908229`
- **Портал 2**:
  - Причины отказов: `UF_CRM_1758612743092`
  - История отказов: `UF_CRM_1758612825886`

### API URLs:
- **Алимакс**: `https://alimaks.bitrix24.ru/rest/53/8w5vxvy0h72qy3sz/`
- **Портал 2**: `https://b24-j9fqpa.bitrix24.ru/rest/9/cu1f85dy254v7guk/`

## 🚀 Установка

### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd bitrix_deal_webhook
```

### 2. Установка зависимостей
```bash
pip3 install -r requirements.txt
```

### 3. Настройка переменных окружения
```bash
export BITRIX_WEBHOOK_URL="https://your-portal.bitrix24.ru/rest/ID/TOKEN/"
export REJECTION_REASON_FIELD="UF_CRM_XXXXX"
export REJECTION_HISTORY_FIELD="UF_CRM_XXXXX"
```

### 4. Настройка Systemd сервиса
```bash
sudo cp bitrix_deal_webhook.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable bitrix_deal_webhook
sudo systemctl start bitrix_deal_webhook
```

### 5. Настройка Apache
```bash
sudo cp bitrix-webhook.conf /etc/apache2/sites-available/
sudo a2ensite bitrix-webhook
sudo systemctl reload apache2
```

### 6. Настройка CRON
```bash
sudo cp bitrix_cron_processor /etc/cron.d/
sudo cp bitrix_webhook_monitor /etc/cron.d/
```

## 📊 Мониторинг

### Логи:
- **Flask приложение**: `journalctl -u bitrix_deal_webhook -f`
- **CRON Алимакс**: `tail -f /var/log/bitrix_cron.log`
- **CRON Портал 2**: `tail -f /var/log/bitrix_cron_portal2.log`

### Статус сервисов:
```bash
sudo systemctl status bitrix_deal_webhook
sudo systemctl status apache2
```

## 🔧 Использование

### Ручной запуск CRON процессора:
```bash
# Алимакс
/root/projects/bitrix_deal_webhook/run_cron.sh

# Портал 2
/root/projects/bitrix_deal_webhook/run_cron_portal2.sh
```

### Тестирование API:
```bash
curl -X POST http://your-server/webhook/deal \
  -H "Content-Type: application/json" \
  -d '{"event": "ONCRMDEALADD", "data": {"FIELDS": {"ID": "12345"}}}'
```

## 🛠️ Устранение неполадок

### Проверка статуса:
```bash
./check_and_fix.sh
```

### Перезапуск сервисов:
```bash
sudo systemctl restart bitrix_deal_webhook
sudo systemctl restart apache2
```

### Очистка логов:
```bash
sudo journalctl --vacuum-time=7d
```

## 📝 Лицензия

MIT License

## 🤝 Поддержка

Для получения поддержки создайте issue в репозитории или обратитесь к администратору системы.