#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки настройки и работоспособности
"""

import os
import sys
import json
import requests
from datetime import datetime

def test_imports():
    """Тест импорта всех необходимых модулей"""
    try:
        import flask
        import requests
        print("✓ Все модули импортированы успешно")
        return True
    except ImportError as e:
        print("✗ Ошибка импорта: {}".format(e))
        return False

def test_config():
    """Тест конфигурации"""
    print("\n=== Проверка конфигурации ===")
    
    # Проверяем .env файл
    env_file = '.env'
    if os.path.exists(env_file):
        print("✓ Файл .env найден")
        
        # Загружаем переменные
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        required_vars = [
            'BITRIX_WEBHOOK_URL',
            'REJECTION_REASON_FIELD',
            'REJECTION_HISTORY_FIELD'
        ]
        
        found_vars = []
        for line in lines:
            if '=' in line and not line.strip().startswith('#'):
                var_name = line.split('=')[0].strip()
                if var_name in required_vars:
                    found_vars.append(var_name)
        
        for var in required_vars:
            if var in found_vars:
                print("✓ {} настроен".format(var))
            else:
                print("✗ {} НЕ настроен".format(var))
        
        return len(found_vars) == len(required_vars)
    else:
        print("✗ Файл .env не найден")
        print("  Скопируйте config.env.example в .env и настройте параметры")
        return False

def test_bitrix_connection():
    """Тест соединения с Битрикс24"""
    print("\n=== Проверка соединения с Битрикс24 ===")
    
    webhook_url = os.getenv('BITRIX_WEBHOOK_URL')
    if not webhook_url:
        print("✗ BITRIX_WEBHOOK_URL не настроен")
        return False
    
    try:
        # Тестовый запрос к API
        test_url = "{}/crm.deal.fields".format(webhook_url.rstrip('/'))
        response = requests.get(test_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'result' in data:
                print("✓ Соединение с Битрикс24 успешно")
                
                # Проверяем наличие настроенных полей
                fields = data['result']
                rejection_field = os.getenv('REJECTION_REASON_FIELD', 'UF_CRM_REJECTION_REASON')
                history_field = os.getenv('REJECTION_HISTORY_FIELD', 'UF_CRM_REJECTION_HISTORY')
                
                if rejection_field in fields:
                    print("✓ Поле причины отказа '{}' найдено".format(rejection_field))
                else:
                    print("✗ Поле причины отказа '{}' НЕ найдено".format(rejection_field))
                    print("  Создайте это поле в настройках CRM")
                
                if history_field in fields:
                    print("✓ Поле истории причин '{}' найдено".format(history_field))
                else:
                    print("✗ Поле истории причин '{}' НЕ найдено".format(history_field))
                    print("  Создайте это поле в настройках CRM")
                
                return True
            else:
                print("✗ Некорректный ответ от API: {}".format(data))
                return False
        else:
            print("✗ Ошибка HTTP {}: {}".format(response.status_code, response.text))
            return False
            
    except requests.exceptions.RequestException as e:
        print("✗ Ошибка соединения: {}".format(e))
        return False

def test_app_startup():
    """Тест запуска приложения"""
    print("\n=== Проверка запуска приложения ===")
    
    try:
        # Импортируем приложение
        sys.path.insert(0, '.')
        from app import init_app, app
        
        # Инициализируем
        if init_app():
            print("✓ Приложение инициализировано успешно")
            
            # Проверяем доступность эндпоинтов
            with app.test_client() as client:
                response = client.get('/health')
                if response.status_code == 200:
                    data = json.loads(response.data)
                    print("✓ Health check работает: {}".format(data['status']))
                    return True
                else:
                    print("✗ Health check не работает")
                    return False
        else:
            print("✗ Ошибка инициализации приложения")
            return False
            
    except Exception as e:
        print("✗ Ошибка запуска: {}".format(e))
        return False

def main():
    """Основная функция тестирования"""
    print("=== Тест настройки Bitrix Deal Webhook ===")
    print("Время: {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    
    tests = [
        ("Импорт модулей", test_imports),
        ("Конфигурация", test_config),
        ("Соединение с Битрикс24", test_bitrix_connection),
        ("Запуск приложения", test_app_startup)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print("\n" + "="*50)
        print("Тест: {}".format(test_name))
        print("="*50)
        
        if test_func():
            passed += 1
    
    print("\n" + "="*50)
    print("ИТОГ: {}/{} тестов пройдено".format(passed, total))
    
    if passed == total:
        print("✓ Все тесты прошли успешно! Система готова к работе.")
        print("\nДля запуска используйте:")
        print("  ./run.sh")
    else:
        print("✗ Некоторые тесты не прошли. Проверьте настройки.")
        print("\nИнструкции по настройке см. в README.md")
    
    print("="*50)

if __name__ == '__main__':
    main()

