#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Битрикс24 Webhook Handler для копирования причин отказов
Обрабатывает создание сделок и копирует причины отказов из предыдущих сделок контакта
"""

import os
import json
import logging
import requests
from datetime import datetime
from flask import Flask, request, jsonify
# from typing import List, Dict, Optional, Any  # Закомментировано для совместимости

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('webhook.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class BitrixAPI:
    """Класс для работы с API Битрикс24"""
    
    def __init__(self, webhook_url):
        """
        Инициализация API клиента
        
        Args:
            webhook_url: URL вебхука для REST API Битрикс24
        """
        self.webhook_url = webhook_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'BitrixDealWebhook/1.0'
        })
    
    def _make_request(self, method, params=None):
        """
        Выполнение запроса к API Битрикс24
        
        Args:
            method: Метод API
            params: Параметры запроса
            
        Returns:
            Ответ API или None в случае ошибки
        """
        try:
            url = "{}/{}".format(self.webhook_url, method)
            response = self.session.post(url, json=params or {})
            response.raise_for_status()
            
            data = response.json()
            if 'error' in data:
                logger.error("API Error: {}".format(data['error']))
                return None
                
            return data.get('result')
            
        except requests.exceptions.RequestException as e:
            logger.error("Request failed: {}".format(e))
            return None
        except json.JSONDecodeError as e:
            logger.error("JSON decode error: {}".format(e))
            return None
    
    def get_deal(self, deal_id):
        """Получение данных сделки"""
        return self._make_request('crm.deal.get', {'id': deal_id})
    
    def get_deals_by_contact(self, contact_id):
        """
        Получение всех сделок контакта
        
        Args:
            contact_id: ID контакта
            
        Returns:
            Список сделок контакта
        """
        deals = []
        start = 0
        
        while True:
            result = self._make_request('crm.deal.list', {
                'filter': {'CONTACT_ID': contact_id},
                'select': ['ID', 'TITLE', 'STAGE_ID', 'DATE_CREATE', 'DATE_MODIFY'] + 
                         [REJECTION_REASON_FIELD],
                'start': start,
                'order': {'DATE_CREATE': 'DESC'}
            })
            
            if not result:
                break
                
            deals.extend(result)
            
            # Проверяем, есть ли еще данные
            if len(result) < 50:  # По умолчанию Битрикс возвращает до 50 записей
                break
                
            start += 50
        
        logger.info("Found {} deals for contact {}".format(len(deals), contact_id))
        return deals
    
    def update_deal(self, deal_id, fields):
        """
        Обновление полей сделки
        
        Args:
            deal_id: ID сделки
            fields: Поля для обновления
            
        Returns:
            True если обновление прошло успешно
        """
        result = self._make_request('crm.deal.update', {
            'id': deal_id,
            'fields': fields
        })
        
        return result is not None

class DealProcessor:
    """Класс для обработки логики сделок"""
    
    def __init__(self, bitrix_api):
        self.api = bitrix_api
    
    def extract_rejection_reasons(self, deals):
        """
        Извлечение причин отказов из списка сделок
        
        Args:
            deals: Список сделок
            
        Returns:
            Список причин отказов (без пустых значений)
        """
        reasons = []
        
        for deal in deals:
            # Проверяем, что сделка имеет статус отказа
            stage_id = deal.get('STAGE_ID', '')
            if not self._is_rejection_stage(stage_id):
                continue
                
            # Извлекаем причину отказа
            reason = deal.get(REJECTION_REASON_FIELD, '')
            if reason:
                reason = str(reason).strip()
                if reason and reason not in reasons:
                    reasons.append(reason)
        
        return reasons
    
    def _is_rejection_stage(self, stage_id):
        """
        Проверка, является ли стадия сделки отказом
        
        Args:
            stage_id: ID стадии сделки
            
        Returns:
            True если стадия является отказом
        """
        # Стандартные стадии отказа в Битрикс24
        rejection_stages = [
            'LOSE',  # Проиграна
            'C1:LOSE',  # Проиграна (воронка 1)
            'C2:LOSE',  # Проиграна (воронка 2)
            'C3:LOSE',  # Проиграна (воронка 3)
        ]
        
        # Добавляем кастомные стадии отказа если они указаны в настройках
        if CUSTOM_REJECTION_STAGES:
            rejection_stages.extend(CUSTOM_REJECTION_STAGES)
        
        return stage_id in rejection_stages
    
    def format_rejection_reasons(self, reasons):
        """
        Форматирование списка причин отказов
        
        Args:
            reasons: Список причин
            
        Returns:
            Отформатированная строка с причинами
        """
        if not reasons:
            return ""
        
        # Нумерованный список причин
        formatted_reasons = []
        for i, reason in enumerate(reasons, 1):
            formatted_reasons.append("{}. {}".format(i, reason))
        
        result = "Предыдущие причины отказов:\n" + "\n".join(formatted_reasons)
        
        # Ограничиваем длину если необходимо
        if len(result) > MAX_FIELD_LENGTH:
            result = result[:MAX_FIELD_LENGTH - 3] + "..."
        
        return result
    
    def process_new_deal(self, deal_id):
        """
        Обработка новой сделки - поиск и копирование причин отказов
        
        Args:
            deal_id: ID новой сделки
            
        Returns:
            True если обработка прошла успешно
        """
        try:
            # Получаем данные новой сделки
            deal = self.api.get_deal(deal_id)
            if not deal:
                logger.error("Failed to get deal {}".format(deal_id))
                return False
            
            # Получаем ID контакта
            contact_id = deal.get('CONTACT_ID')
            if not contact_id:
                logger.info("Deal {} has no contact, skipping".format(deal_id))
                return True
            
            logger.info("Processing deal {} for contact {}".format(deal_id, contact_id))
            
            # Получаем все сделки контакта (кроме текущей)
            all_deals = self.api.get_deals_by_contact(contact_id)
            previous_deals = [d for d in all_deals if int(d['ID']) != deal_id]
            
            if not previous_deals:
                logger.info("No previous deals found for contact {}".format(contact_id))
                return True
            
            # Извлекаем причины отказов
            rejection_reasons = self.extract_rejection_reasons(previous_deals)
            
            if not rejection_reasons:
                logger.info("No rejection reasons found for contact {}".format(contact_id))
                return True
            
            # Форматируем и записываем в поле сделки
            formatted_reasons = self.format_rejection_reasons(rejection_reasons)
            
            success = self.api.update_deal(deal_id, {
                REJECTION_HISTORY_FIELD: formatted_reasons
            })
            
            if success:
                logger.info("Successfully updated deal {} with {} rejection reasons".format(deal_id, len(rejection_reasons)))
            else:
                logger.error("Failed to update deal {}".format(deal_id))
            
            return success
            
        except Exception as e:
            logger.error("Error processing deal {}: {}".format(deal_id, e))
            return False

# Глобальные настройки (будут загружены из переменных окружения)
BITRIX_WEBHOOK_URL = os.getenv('BITRIX_WEBHOOK_URL', '')
REJECTION_REASON_FIELD = os.getenv('REJECTION_REASON_FIELD', 'UF_CRM_REJECTION_REASON')
REJECTION_HISTORY_FIELD = os.getenv('REJECTION_HISTORY_FIELD', 'UF_CRM_REJECTION_HISTORY')
MAX_FIELD_LENGTH = int(os.getenv('MAX_FIELD_LENGTH', '2000'))
CUSTOM_REJECTION_STAGES = os.getenv('CUSTOM_REJECTION_STAGES', '').split(',') if os.getenv('CUSTOM_REJECTION_STAGES') else []

# Инициализация компонентов
bitrix_api = None
deal_processor = None

def init_app():
    """Инициализация приложения"""
    global bitrix_api, deal_processor
    
    if not BITRIX_WEBHOOK_URL:
        logger.error("BITRIX_WEBHOOK_URL not configured")
        return False
    
    bitrix_api = BitrixAPI(BITRIX_WEBHOOK_URL)
    deal_processor = DealProcessor(bitrix_api)
    
    logger.info("Application initialized successfully")
    return True

@app.route('/health', methods=['GET'])
def health_check():
    """Проверка работоспособности сервиса"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'configured': bool(BITRIX_WEBHOOK_URL)
    })

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

@app.route('/test/deal/<int:deal_id>', methods=['POST'])
def test_deal_processing(deal_id):
    """
    Тестовый endpoint для проверки обработки сделки
    Полезно для отладки без вебхуков
    """
    if not deal_processor:
        return jsonify({'error': 'Service not configured'}), 500
    
    success = deal_processor.process_new_deal(deal_id)
    
    if success:
        return jsonify({'message': 'Deal {} processed successfully'.format(deal_id)}), 200
    else:
        return jsonify({'error': 'Failed to process deal {}'.format(deal_id)}), 500

@app.route('/test/webhook', methods=['POST'])
def test_webhook():
    """
    Тестовый endpoint для проверки вебхука
    """
    try:
        logger.info("=== TEST WEBHOOK RECEIVED ===")
        logger.info("Headers: {}".format(dict(request.headers)))
        logger.info("Raw data: {}".format(request.get_data()))
        logger.info("JSON data: {}".format(request.get_json()))
        logger.info("=============================")
        
        return jsonify({
            'message': 'Test webhook received successfully',
            'timestamp': datetime.now().isoformat(),
            'headers': dict(request.headers),
            'data': request.get_json()
        }), 200
        
    except Exception as e:
        logger.error("Test webhook error: {}".format(e))
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

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Инициализация при запуске модуля
init_app()

if __name__ == '__main__':
    if bitrix_api and deal_processor:
        # Запуск в режиме разработки
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        logger.error("Failed to initialize application")
        exit(1)
