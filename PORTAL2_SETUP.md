# Настройка второго портала Битрикс24

## 🎯 **Конфигурация:**

- **Портал**: `b24-j9fqpa.bitrix24.ru`
- **API URL**: `https://b24-j9fqpa.bitrix24.ru/rest/9/cu1f85dy254v7guk/`
- **Поле причин отказов**: `UF_CRM_1758612743092`
- **Поле истории отказов**: `UF_CRM_1758612825886`

## ✅ **Статус:**

- ✅ **CRON-процессор создан**: `cron_processor_portal2.py`
- ✅ **Скрипт-обертка**: `run_cron_portal2.sh`
- ✅ **CRON-задача настроена**: Каждую минуту
- ✅ **API работает**: Доступ к сделкам и контактам
- ✅ **Логирование**: `/var/log/bitrix_cron_portal2.log`

## 🔧 **Файлы:**

1. **`cron_processor_portal2.py`** - Основной процессор
2. **`run_cron_portal2.sh`** - Скрипт-обертка
3. **`/var/log/bitrix_cron_portal2.log`** - Логи

## 📋 **CRON-задача:**

```bash
* * * * * /root/projects/bitrix_deal_webhook/run_cron_portal2.sh >> /var/log/bitrix_cron_portal2.log 2>&1
```

## 🚀 **Как работает:**

1. **Каждую минуту** CRON запускает процессор
2. **Процессор находит** новые сделки за последний час
3. **Для каждой сделки** проверяет контакта
4. **Собирает причины отказов** из предыдущих сделок
5. **Заполняет поле** `UF_CRM_1758612825886`

## 📊 **Мониторинг:**

```bash
# Просмотр логов
tail -f /var/log/bitrix_cron_portal2.log

# Проверка CRON-задач
crontab -l

# Ручной запуск
/root/projects/bitrix_deal_webhook/run_cron_portal2.sh
```

## ✅ **Готово к работе!**


