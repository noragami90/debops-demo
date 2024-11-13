from flask import Flask, render_template, jsonify
import socket
import datetime
import logging
from prometheus_client import Counter, generate_latest

# Метрики Prometheus
REQUESTS = Counter('http_requests_total', 'Total number of HTTP requests')

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    try:
        REQUESTS.inc()  # Увеличиваем счетчик запросов
        hostname = socket.gethostname()
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"Request received. Hostname: {hostname}")
        return render_template('index.html',
                             hostname=hostname,
                             current_time=current_time)
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        return str(e), 500

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'version': '1.1'
    })

@app.route('/metrics')
def metrics():
    return generate_latest()

if __name__ == '__main__':
    logger.info("Starting application...")
    app.run(host='0.0.0.0', port=5000)