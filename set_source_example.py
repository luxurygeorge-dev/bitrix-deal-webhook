#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пример скрипта для установки источника в сделку
"""

import requests
import json

# Настройки
WEBHOOK_URL = "https://promarketing1.bitrix24.ru/rest/9/fxn8xyfbalblll9s"

def set_deal_source(deal_id, source_id):
    """
    Установить источник для сделки
    
    Args:
        deal_id: ID сделки
        source_id: ID источника (см. sources_reference.txt)
    """
    
    print("Установка источника '{}' для сделки {}...".format(source_id, deal_id))
    
    try:
        url = "{}/crm.deal.update".format(WEBHOOK_URL)
        params = {
            'id': deal_id,
            'fields': {
                'SOURCE_ID': source_id
            }
        }
        
        response = requests.post(url, json=params)
        response.raise_for_status()
        
        data = response.json()
        
        if 'result' in data and data['result']:
            print("✓ Источник успешно установлен!")
            return True
        else:
            print("✗ Ошибка: {}".format(data.get('error_description', 'Неизвестная ошибка')))
            return False
            
    except requests.exceptions.RequestException as e:
        print("✗ Ошибка запроса: {}".format(e))
        return False
    except Exception as e:
        print("✗ Неожиданная ошибка: {}".format(e))
        return False

def create_deal_with_source(title, contact_id, source_id):
    """
    Создать сделку с указанным источником
    
    Args:
        title: Название сделки
        contact_id: ID контакта
        source_id: ID источника
    """
    
    print("Создание сделки '{}' с источником '{}'...".format(title, source_id))
    
    try:
        url = "{}/crm.deal.add".format(WEBHOOK_URL)
        params = {
            'fields': {
                'TITLE': title,
                'CONTACT_ID': contact_id,
                'SOURCE_ID': source_id
            }
        }
        
        response = requests.post(url, json=params)
        response.raise_for_status()
        
        data = response.json()
        
        if 'result' in data:
            deal_id = data['result']
            print("✓ Сделка создана с ID: {}".format(deal_id))
            return deal_id
        else:
            print("✗ Ошибка: {}".format(data.get('error_description', 'Неизвестная ошибка')))
            return None
            
    except requests.exceptions.RequestException as e:
        print("✗ Ошибка запроса: {}".format(e))
        return None
    except Exception as e:
        print("✗ Неожиданная ошибка: {}".format(e))
        return None

def get_deal_info(deal_id):
    """Получить информацию о сделке включая источник"""
    
    try:
        url = "{}/crm.deal.get".format(WEBHOOK_URL)
        params = {
            'id': deal_id
        }
        
        response = requests.post(url, json=params)
        response.raise_for_status()
        
        data = response.json()
        
        if 'result' in data:
            deal = data['result']
            title = deal.get('TITLE', 'Без названия')
            source_id = deal.get('SOURCE_ID', 'Не указан')
            contact_id = deal.get('CONTACT_ID', 'Не указан')
            
            print("Информация о сделке {}:".format(deal_id))
            print("  Название: {}".format(title))
            print("  Источник: {}".format(source_id))
            print("  Контакт: {}".format(contact_id))
            
            return deal
        else:
            print("✗ Сделка не найдена")
            return None
            
    except Exception as e:
        print("✗ Ошибка получения сделки: {}".format(e))
        return None

def main():
    """Примеры использования"""
    
    print("=== Примеры работы с источниками сделок ===\n")
    
    print("Доступные источники:")
    sources = [
        ("CALL", "Сайт"),
        ("WEBFORM", "Яндекс.Карты"), 
        ("CALLBACK", "2ГИС"),
        ("RC_GENERATOR", "Авито"),
        ("STORE", "По рекомендации"),
        ("REPEAT_SALE", "Яндекс.Услуги"),
        ("1", "Партнеры"),
        ("2", "Яндекс.Контекст"),
        ("BOOKING", "Онлайн-запись"),
        ("3", "Соц. сети")
    ]
    
    for source_id, name in sources:
        print("  {} -> {}".format(source_id, name))
    
    print("\n" + "="*50)
    print("Для использования замените значения ниже:")
    print("="*50)
    
    # ПРИМЕРЫ - ЗАМЕНИТЕ НА РЕАЛЬНЫЕ ЗНАЧЕНИЯ!
    
    # Пример 1: Обновить источник существующей сделки
    # deal_id = 1234  # Замените на ID реальной сделки
    # source_id = "CALL"  # Источник "Сайт"
    # set_deal_source(deal_id, source_id)
    
    # Пример 2: Создать сделку с источником
    # contact_id = 567  # Замените на ID реального контакта  
    # create_deal_with_source("Тестовая сделка", contact_id, "2")  # Яндекс.Контекст
    
    # Пример 3: Проверить источник сделки
    # get_deal_info(1234)
    
    print("Раскомментируйте нужные строки и укажите реальные ID!")

if __name__ == '__main__':
    main()
