#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для получения списка источников из Битрикс24
"""

import json
import requests
from datetime import datetime

# Вебхук клиента
WEBHOOK_URL = "https://promarketing1.bitrix24.ru/rest/9/fxn8xyfbalblll9s"

def get_deal_sources():
    """Получить список источников для сделок"""
    print("=== Получение источников сделок ===")
    
    try:
        url = "{}/crm.status.list".format(WEBHOOK_URL)
        params = {
            'filter': {
                'ENTITY_ID': 'SOURCE'
            }
        }
        
        response = requests.post(url, json=params)
        response.raise_for_status()
        
        data = response.json()
        
        if 'result' in data:
            sources = data['result']
            
            print("Найдено {} источников для сделок:".format(len(sources)))
            print("-" * 60)
            
            for source in sources:
                status_id = source.get('STATUS_ID', 'N/A')
                name = source.get('NAME', 'Без названия')
                sort = source.get('SORT', 'N/A')
                
                print("ID: {} | Название: {} | Сортировка: {}".format(
                    status_id, name, sort
                ))
            
            return sources
        else:
            print("Ошибка в ответе API: {}".format(data))
            return []
            
    except requests.exceptions.RequestException as e:
        print("Ошибка запроса: {}".format(e))
        return []
    except Exception as e:
        print("Неожиданная ошибка: {}".format(e))
        return []

def get_contact_sources():
    """Получить список источников для контактов"""
    print("\n=== Получение источников контактов ===")
    
    try:
        url = "{}/crm.status.list".format(WEBHOOK_URL)
        params = {
            'filter': {
                'ENTITY_ID': 'SOURCE_CONTACT'
            }
        }
        
        response = requests.post(url, json=params)
        response.raise_for_status()
        
        data = response.json()
        
        if 'result' in data:
            sources = data['result']
            
            print("Найдено {} источников для контактов:".format(len(sources)))
            print("-" * 60)
            
            for source in sources:
                status_id = source.get('STATUS_ID', 'N/A')
                name = source.get('NAME', 'Без названия')
                sort = source.get('SORT', 'N/A')
                
                print("ID: {} | Название: {} | Сортировка: {}".format(
                    status_id, name, sort
                ))
            
            return sources
        else:
            print("Ошибка в ответе API: {}".format(data))
            return []
            
    except requests.exceptions.RequestException as e:
        print("Ошибка запроса: {}".format(e))
        return []
    except Exception as e:
        print("Неожиданная ошибка: {}".format(e))
        return []

def get_lead_sources():
    """Получить список источников для лидов"""
    print("\n=== Получение источников лидов ===")
    
    try:
        url = "{}/crm.status.list".format(WEBHOOK_URL)
        params = {
            'filter': {
                'ENTITY_ID': 'SOURCE_LEAD'
            }
        }
        
        response = requests.post(url, json=params)
        response.raise_for_status()
        
        data = response.json()
        
        if 'result' in data:
            sources = data['result']
            
            print("Найдено {} источников для лидов:".format(len(sources)))
            print("-" * 60)
            
            for source in sources:
                status_id = source.get('STATUS_ID', 'N/A')
                name = source.get('NAME', 'Без названия')
                sort = source.get('SORT', 'N/A')
                
                print("ID: {} | Название: {} | Сортировка: {}".format(
                    status_id, name, sort
                ))
            
            return sources
        else:
            print("Ошибка в ответе API: {}".format(data))
            return []
            
    except requests.exceptions.RequestException as e:
        print("Ошибка запроса: {}".format(e))
        return []
    except Exception as e:
        print("Неожиданная ошибка: {}".format(e))
        return []

def save_sources_to_json(deal_sources, contact_sources, lead_sources):
    """Сохранить все источники в JSON файл"""
    
    data = {
        'timestamp': datetime.now().isoformat(),
        'webhook_url': WEBHOOK_URL,
        'sources': {
            'deals': deal_sources,
            'contacts': contact_sources,
            'leads': lead_sources
        }
    }
    
    filename = 'bitrix_sources_{}.json'.format(datetime.now().strftime('%Y%m%d_%H%M%S'))
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print("\n✓ Данные сохранены в файл: {}".format(filename))
        return filename
    except Exception as e:
        print("\n✗ Ошибка сохранения: {}".format(e))
        return None

def create_sources_reference():
    """Создать справочный файл с источниками"""
    
    deal_sources = get_deal_sources()
    contact_sources = get_contact_sources()
    lead_sources = get_lead_sources()
    
    # Создаем текстовый справочник
    reference = []
    reference.append("=" * 80)
    reference.append("СПРАВОЧНИК ИСТОЧНИКОВ БИТРИКС24")
    reference.append("Портал: promarketing1.bitrix24.ru")
    reference.append("Время: {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    reference.append("=" * 80)
    
    if deal_sources:
        reference.append("\n📋 ИСТОЧНИКИ ДЛЯ СДЕЛОК (SOURCE):")
        reference.append("-" * 50)
        for source in deal_sources:
            reference.append("  ID: {} -> {}".format(
                source.get('STATUS_ID', 'N/A'),
                source.get('NAME', 'Без названия')
            ))
    
    if contact_sources:
        reference.append("\n👤 ИСТОЧНИКИ ДЛЯ КОНТАКТОВ (SOURCE_CONTACT):")
        reference.append("-" * 50)
        for source in contact_sources:
            reference.append("  ID: {} -> {}".format(
                source.get('STATUS_ID', 'N/A'),
                source.get('NAME', 'Без названия')
            ))
    
    if lead_sources:
        reference.append("\n🎯 ИСТОЧНИКИ ДЛЯ ЛИДОВ (SOURCE_LEAD):")
        reference.append("-" * 50)
        for source in lead_sources:
            reference.append("  ID: {} -> {}".format(
                source.get('STATUS_ID', 'N/A'),
                source.get('NAME', 'Без названия')
            ))
    
    reference.append("\n" + "=" * 80)
    reference.append("Примеры использования:")
    reference.append("")
    reference.append("# Создание сделки с источником:")
    reference.append("curl -X POST '{}/crm.deal.add' \\".format(WEBHOOK_URL))
    reference.append("  -H 'Content-Type: application/json' \\")
    reference.append("  -d '{")
    reference.append('    "fields": {')
    reference.append('      "TITLE": "Тестовая сделка",')
    reference.append('      "SOURCE_ID": "1",  # Замените на нужный ID')
    reference.append('      "CONTACT_ID": 123')
    reference.append('    }')
    reference.append('  }"')
    reference.append("")
    reference.append("# Обновление источника существующей сделки:")
    reference.append("curl -X POST '{}/crm.deal.update' \\".format(WEBHOOK_URL))
    reference.append("  -H 'Content-Type: application/json' \\")
    reference.append("  -d '{")
    reference.append('    "id": 456,  # ID сделки')
    reference.append('    "fields": {')
    reference.append('      "SOURCE_ID": "2"  # Новый источник')
    reference.append('    }')
    reference.append('  }"')
    reference.append("=" * 80)
    
    # Сохраняем справочник
    filename = 'sources_reference.txt'
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(reference))
        
        print("\n✓ Справочник сохранен в файл: {}".format(filename))
    except Exception as e:
        print("\n✗ Ошибка сохранения справочника: {}".format(e))
    
    # Сохраняем JSON
    save_sources_to_json(deal_sources, contact_sources, lead_sources)
    
    return deal_sources, contact_sources, lead_sources

def main():
    """Основная функция"""
    print("Получение списка источников из Битрикс24")
    print("Портал: promarketing1.bitrix24.ru")
    print("=" * 60)
    
    deal_sources, contact_sources, lead_sources = create_sources_reference()
    
    print("\n🎉 ГОТОВО!")
    print("Проверьте файлы:")
    print("  - sources_reference.txt (текстовый справочник)")
    print("  - bitrix_sources_*.json (данные в JSON)")

if __name__ == '__main__':
    main()
