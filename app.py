#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask приложение для обработки вебхуков Битрикс24
Автоматически заполняет поля "Предыдущие причины отказов" в сделках
"""

import os
import json
import logging
import requests
from flask import Flask, request, jsonify
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/bitrix_webhook.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class BitrixAPI:
    """Класс для работы с API Битрикс24"""
    
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'BitrixWebhookHandler/1.0'
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

class DealProcessor:
    """Процессор для обработки сделок"""
    
    def __init__(self, api_client):
        self.api = api_client
        self.rejection_history_field = os.getenv('REJECTION_HISTORY_FIELD', 'UF_CRM_1755175908229')
        self.max_field_length = int(os.getenv('MAX_FIELD_LENGTH', '2000'))
    
    def get_contact_rejection_reasons(self, contact_id):
        """Получение причин отказов из поля контакта"""
        try:
            # Получаем контакт
            contact_data = self.api._make_request('crm.contact.get', {'ID': contact_id})
            if not contact_data or 'result' not in contact_data:
                return []
            
            contact = contact_data['result']
            rejection_field = contact.get('UF_CRM_1755175983293', '')
            
            if not rejection_field:
                return []
            
            # Если это строка, разбиваем по переносам строк
            if isinstance(rejection_field, str):
                reasons = [line.strip() for line in rejection_field.split('\n') if line.strip()]
            else:
                reasons = [str(rejection_field).strip()]
            
            return [r for r in reasons if r]
            
        except Exception as e:
            logger.error(f"Error getting contact rejection reasons: {e}")
            return []
    
    def process_new_deal(self, deal_id):
        """Обработка новой сделки"""
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
            
            # Получаем причины отказов из поля контакта
            rejection_reasons = self.get_contact_rejection_reasons(contact_id)
            logger.info(f"Found {len(rejection_reasons)} rejection reasons in contact {contact_id}")
            
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

# Инициализация API клиента
webhook_url = os.getenv('BITRIX_WEBHOOK_URL')
if webhook_url:
    api = BitrixAPI(webhook_url)
    deal_processor = DealProcessor(api)
    logger.info("Deal processor initialized")
else:
    logger.error("BITRIX_WEBHOOK_URL not configured")
    deal_processor = None

@app.route('/webhook/deal', methods=['POST'])
def deal_webhook():
    """
    Обработчик вебхука для событий сделок
    Ожидает события создания сделки от Битрикс24
    """
    try:
        if not deal_processor:
            return jsonify({'error': 'Service not configured'}), 500
        
        # Получаем данные вебхука
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Логируем ВСЕ входящие запросы для отладки
        logger.info("=== WEBHOOK RECEIVED ===")
        logger.info("Headers: {}".format(dict(request.headers)))
        logger.info("Raw data: {}".format(request.get_data()))
        logger.info("JSON data: {}".format(json.dumps(data, ensure_ascii=False)))
        logger.info("========================")
        
        # Извлекаем информацию о событии
        event = data.get('event')
        deal_id = data.get('data', {}).get('FIELDS', {}).get('ID')
        auth_data = data.get('auth', {})

        if event not in ['ONCRMDEALADD', 'ONCRMDEALUPDATE']:
            logger.info("Ignoring event {}".format(event))
            return jsonify({'message': 'Event ignored'}), 200
        
        if not deal_id:
            return jsonify({'error': 'Deal ID not found'}), 400
        
        deal_id = int(deal_id)
        
        # Исходящие вебхуки не предоставляют API токены, используем глобальный API клиент
        logger.info("Processing deal {} with global API client".format(deal_id))
        success = deal_processor.process_new_deal(deal_id)
        
        if success:
            return jsonify({'message': 'Deal processed successfully'}), 200
        else:
            return jsonify({'error': 'Failed to process deal'}), 500
            
    except Exception as e:
        logger.error("Webhook processing error: {}".format(e))
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/webhook', methods=['POST'])
def webhook_universal():
    """
    Универсальный хендлер для вебхуков
    """
    return deal_webhook()

@app.route('/bitrix/webhook', methods=['POST'])
def bitrix_webhook():
    """
    Специфичный хендлер для Битрикс24
    """
    return deal_webhook()

@app.route('/bitrix/webhook/deal', methods=['POST'])
def bitrix_deal_webhook():
    """
    Альтернативный хендлер для сделок Битрикс24
    """
    return deal_webhook()

@app.route('/api/webhook', methods=['POST'])
def api_webhook():
    """
    API хендлер для вебхуков
    """
    return deal_webhook()

@app.route('/api/webhook/deal', methods=['POST'])
def api_deal_webhook():
    """
    API хендлер для сделок
    """
    return deal_webhook()

@app.route('/health', methods=['GET'])
def health_check():
    """Проверка здоровья сервиса"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'webhook_configured': deal_processor is not None
    })

@app.route('/', methods=['GET'])
def root():
    """Корневой маршрут"""
    return jsonify({
        'service': 'Bitrix24 Deal Webhook Handler',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': [
            '/webhook/deal',
            '/webhook',
            '/bitrix/webhook',
            '/bitrix/webhook/deal',
            '/api/webhook',
            '/api/webhook/deal',
            '/health'
        ]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)