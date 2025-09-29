# Bitrix24 Deal Webhook System

Автоматическая система для заполнения полей "Предыдущие причины отказов" в сделках Битрикс24.

## 🎯 Описание

Система автоматически:
- Находит новые сделки в Битрикс24
- Собирает причины отказов из поля контакта
- Заполняет поле "Предыдущие причины отказов" в новых сделках

## 🏗️ Архитектура

### Компоненты:
1. **Flask Webhook Handler** (`app.py`) - Обработка входящих вебхуков
2. **CRON Processor** - Резервная система для обработки сделок
3. **Systemd Service** - Управление Flask приложением
4. **Apache Reverse Proxy** - HTTPS и маршрутизация

## 📁 Структура проекта

```
bitrix_deal_webhook/
├── app.py                          # Основное Flask приложение
├── cron_processor.py               # CRON процессор
├── run_cron.sh                     # Скрипт-обертка для CRON
├── monitor.sh                      # Мониторинг сервиса
├── check_and_fix.sh                # Диагностика и исправление
├── requirements.txt                # Python зависимости
└── README.md                       # Этот файл
```

## ⚙️ Конфигурация

### Поля Битрикс24:
- **Поле контакта с причинами отказов**: `UF_CRM_1755175983293`
- **Поле сделки для истории отказов**: `UF_CRM_1755175908229`

### Переменные окружения:
- `BITRIX_WEBHOOK_URL` - URL входящего вебхука Битрикс24
- `REJECTION_HISTORY_FIELD` - Поле для истории отказов в сделке
- `MAX_FIELD_LENGTH` - Максимальная длина поля (по умолчанию 2000)

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
- **CRON процессор**: `tail -f /var/log/bitrix_cron.log`

### Статус сервисов:
```bash
sudo systemctl status bitrix_deal_webhook
sudo systemctl status apache2
```

## 🔧 Использование

### Ручной запуск CRON процессора:
```bash
/root/projects/bitrix_deal_webhook/run_cron.sh
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