#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRON-процессор для автоматической обработки новых сделок
Проверяет новые сделки каждые 5 минут и заполняет причины отказов
"""

import os
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/bitrix_cron_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BitrixAPI:
    """Класс для работы с API Битрикс24"""
    
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'BitrixCronProcessor/1.0'
        })
    
    def _make_request(self, method, params=None):
        """Выполнение запроса к API Битрикс24"""
        url = f"{self.webhook_url}/{method}.json"
        try:
            response = self.session.post(url, json=params or {})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return None
    
    def get_deal(self, deal_id):
        """Получение сделки по ID"""
        return self._make_request('crm.deal.get', {'ID': deal_id})
    
    def update_deal(self, deal_id, fields):
        """Обновление сделки"""
        return self._make_request('crm.deal.update', {'ID': deal_id, 'fields': fields})
    
    def get_contact_deals(self, contact_id, limit=50):
        """Получение сделок контакта"""
        return self._make_request('crm.deal.list', {
            'filter': {'CONTACT_ID': contact_id},
            'select': ['ID', 'TITLE', 'STAGE_ID', 'UF_CRM_1747809816933'],
            'order': {'DATE_CREATE': 'DESC'},
            'start': 0
        })

class DealProcessor:
    """Процессор для обработки сделок"""
    
    def __init__(self, api_client):
        self.api = api_client
        self.rejection_reason_field = os.getenv('REJECTION_REASON_FIELD', 'UF_CRM_1747809816933')
        self.rejection_history_field = os.getenv('REJECTION_HISTORY_FIELD', 'UF_CRM_1755175908229')
        self.max_field_length = int(os.getenv('MAX_FIELD_LENGTH', '2000'))
        self.rejection_stages = os.getenv('CUSTOM_REJECTION_STAGES', 'LOSE').split(',')
    
    def extract_rejection_reasons(self, deals):
        """Извлечение причин отказов из сделок"""
        reasons = []
        
        for deal in deals:
            # Пропускаем текущую сделку
            if deal.get('STAGE_ID') in self.rejection_stages:
                reason = deal.get(self.rejection_reason_field, '')
                if reason:
                    reason = str(reason).strip()
                    if reason and reason not in reasons:
                        reasons.append(reason)
        
        return reasons
    
    def process_deal(self, deal_id):
        """Обработка конкретной сделки"""
        try:
            logger.info(f"Processing deal {deal_id}")
            
            # Получаем сделку
            deal_data = self.api.get_deal(deal_id)
            if not deal_data or 'result' not in deal_data:
                logger.error(f"Failed to get deal {deal_id}")
                return False
            
            deal = deal_data['result']
            contact_id = deal.get('CONTACT_ID')
            
            if not contact_id:
                logger.warning(f"Deal {deal_id} has no contact")
                return False
            
            logger.info(f"Processing deal {deal_id} for contact {contact_id}")
            
            # Получаем все сделки контакта
            deals_data = self.api.get_contact_deals(contact_id)
            if not deals_data or 'result' not in deals_data:
                logger.error(f"Failed to get deals for contact {contact_id}")
                return False
            
            deals = deals_data['result']
            logger.info(f"Found {len(deals)} deals for contact {contact_id}")
            
            # Извлекаем причины отказов
            rejection_reasons = self.extract_rejection_reasons(deals)
            
            if not rejection_reasons:
                logger.info(f"No rejection reasons found for contact {contact_id}")
                return True
            
            # Формируем текст для поля истории
            history_text = "Предыдущие причины отказов:\n"
            for i, reason in enumerate(rejection_reasons, 1):
                history_text += f"{i}. {reason}\n"
            
            # Обрезаем до максимальной длины
            if len(history_text) > self.max_field_length:
                history_text = history_text[:self.max_field_length-3] + "..."
            
            # Обновляем сделку
            update_result = self.api.update_deal(deal_id, {
                self.rejection_history_field: [history_text]
            })
            
            if update_result and update_result.get('result'):
                logger.info(f"Successfully updated deal {deal_id} with {len(rejection_reasons)} rejection reasons")
                return True
            else:
                logger.error(f"Failed to update deal {deal_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error processing deal {deal_id}: {e}")
            return False

def get_recent_deals(api_client, hours=1):
    """Получение недавно созданных сделок"""
    try:
        # Получаем сделки за последний час
        since = datetime.now() - timedelta(hours=hours)
        since_str = since.strftime('%Y-%m-%d %H:%M:%S')
        
        result = api_client._make_request('crm.deal.list', {
            'filter': {
                '>DATE_CREATE': since_str,
                'STAGE_ID': 'NEW'  # Только новые сделки
            },
            'select': ['ID', 'TITLE', 'CONTACT_ID', 'DATE_CREATE'],
            'order': {'DATE_CREATE': 'DESC'},
            'start': 0
        })
        
        if result and 'result' in result:
            return result['result']
        return []
        
    except Exception as e:
        logger.error(f"Error getting recent deals: {e}")
        return []

def main():
    """Основная функция"""
    try:
        logger.info("=== CRON PROCESSOR STARTED ===")
        
        # Инициализация API
        webhook_url = os.getenv('BITRIX_WEBHOOK_URL')
        if not webhook_url:
            logger.error("BITRIX_WEBHOOK_URL not configured")
            return
        
        api = BitrixAPI(webhook_url)
        processor = DealProcessor(api)
        
        # Получаем недавние сделки
        recent_deals = get_recent_deals(api, hours=1)
        logger.info(f"Found {len(recent_deals)} recent deals")
        
        processed_count = 0
        for deal in recent_deals:
            deal_id = deal['ID']
            logger.info(f"Processing recent deal {deal_id}: {deal['TITLE']}")
            
            if processor.process_deal(deal_id):
                processed_count += 1
        
        logger.info(f"=== CRON PROCESSOR COMPLETED: {processed_count} deals processed ===")
        
    except Exception as e:
        logger.error(f"CRON processor error: {e}")

if __name__ == "__main__":
    main()


