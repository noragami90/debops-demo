from flask import Flask, render_template
import socket
import datetime
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    try:
        hostname = socket.gethostname()
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"Request received. Hostname: {hostname}")
        return render_template('index.html', hostname=hostname, current_time=current_time)
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        return str(e), 500

if __name__ == '__main__':
    logger.info("Starting application...")
    app.run(host='0.0.0.0', port=5000)