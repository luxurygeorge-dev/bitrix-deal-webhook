#!/usr/bin/env python3
"""
Автоматическая проверка новых сделок с Дмитрием
Запускается каждые 2 минуты и проверяет незаполненные сделки
"""

import os
import sys
import time
import requests
import json
from datetime import datetime, timedelta

# Добавляем путь к модулям
sys.path.append('/root/projects/bitrix_deal_webhook')

from app import bitrix_api, deal_processor

def check_recent_deals():
    """Проверяет последние сделки с Дмитрием"""
    try:
        # Получаем последние сделки с Дмитрием за последние 10 минут
        url = f"{os.getenv('BITRIX_WEBHOOK_URL')}/crm.deal.list"
        params = {
            'select[0]': 'ID',
            'select[1]': 'TITLE', 
            'select[2]': 'CONTACT_ID',
            'select[3]': 'DATE_CREATE',
            'select[4]': 'UF_CRM_1755175908229',
            'filter[CONTACT_ID]': '12723',  # Дмитрий
            'order[DATE_CREATE]': 'DESC',
            'start': 0
        }
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if 'result' not in data:
            print(f"Error: {data}")
            return
            
        deals = data['result']
        print(f"Found {len(deals)} deals for Dmitry")
        
        # Проверяем каждую сделку
        for deal in deals:
            deal_id = deal['ID']
            rejection_field = deal.get('UF_CRM_1755175908229', [])
            
            # Если поле пустое, обрабатываем сделку
            if not rejection_field or rejection_field == []:
                print(f"Processing deal {deal_id} - field is empty")
                success = deal_processor.process_new_deal(int(deal_id))
                if success:
                    print(f"Successfully processed deal {deal_id}")
                else:
                    print(f"Failed to process deal {deal_id}")
            else:
                print(f"Deal {deal_id} already processed")
                
    except Exception as e:
        print(f"Error checking deals: {e}")

def main():
    """Основная функция"""
    print(f"Auto-checker started at {datetime.now()}")
    
    while True:
        try:
            check_recent_deals()
            print(f"Check completed at {datetime.now()}")
        except Exception as e:
            print(f"Error in main loop: {e}")
        
        # Ждем 2 минуты
        time.sleep(120)

if __name__ == '__main__':
    main()


