#!/usr/bin/env python3
"""
Скрипт для детальной диагностики вебхука
Логирует ВСЕ входящие запросы в файл
"""

import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/bitrix_webhook_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@app.route('/debug/webhook', methods=['GET', 'POST', 'PUT', 'DELETE'])
def debug_webhook():
    """Обработчик для детальной диагностики"""
    timestamp = datetime.now().isoformat()
    
    # Логируем ВСЕ детали запроса
    logger.info("=" * 80)
    logger.info(f"DEBUG WEBHOOK - {timestamp}")
    logger.info(f"Method: {request.method}")
    logger.info(f"URL: {request.url}")
    logger.info(f"Headers: {dict(request.headers)}")
    logger.info(f"Remote IP: {request.remote_addr}")
    logger.info(f"User-Agent: {request.headers.get('User-Agent', 'Unknown')}")
    
    # Логируем данные
    if request.is_json:
        data = request.get_json()
        logger.info(f"JSON Data: {json.dumps(data, ensure_ascii=False, indent=2)}")
    else:
        raw_data = request.get_data()
        logger.info(f"Raw Data: {raw_data}")
        logger.info(f"Form Data: {dict(request.form)}")
    
    logger.info("=" * 80)
    
    return jsonify({
        'status': 'received',
        'timestamp': timestamp,
        'method': request.method,
        'data_received': True
    })

@app.route('/debug/status', methods=['GET'])
def debug_status():
    """Статус отладки"""
    return jsonify({
        'debug_mode': True,
        'timestamp': datetime.now().isoformat(),
        'endpoints': {
            'debug_webhook': '/debug/webhook',
            'status': '/debug/status'
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)


