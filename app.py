from flask import Flask, render_template, jsonify, request
import socket
import datetime
import logging
import time
import psutil
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Базовые метрики
REQUEST_COUNT = Counter('http_requests_total', 'Total number of HTTP requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'Request latency in seconds', ['endpoint'])
ACTIVE_REQUESTS = Gauge('active_requests', 'Number of active requests')

# Метрики CPU
CPU_USAGE = Gauge('cpu_usage_percent', 'CPU Usage in percent')
CPU_SYSTEM = Gauge('cpu_system_percent', 'System CPU Usage in percent')
CPU_USER = Gauge('cpu_user_percent', 'User CPU Usage in percent')
CPU_CORES = Gauge('cpu_cores_total', 'Number of CPU cores')

# Метрики памяти
MEMORY_USAGE = Gauge('memory_usage_bytes', 'Memory usage in bytes')
MEMORY_TOTAL = Gauge('memory_total_bytes', 'Total memory in bytes')
MEMORY_AVAILABLE = Gauge('memory_available_bytes', 'Available memory in bytes')
MEMORY_CACHED = Gauge('memory_cached_bytes', 'Cached memory in bytes')
MEMORY_SWAP_USED = Gauge('memory_swap_used_bytes', 'Swap memory used in bytes')
MEMORY_SWAP_TOTAL = Gauge('memory_swap_total_bytes', 'Total swap memory in bytes')

# Метрики диска
DISK_USAGE = Gauge('disk_usage_bytes', 'Disk usage in bytes', ['mountpoint'])
DISK_TOTAL = Gauge('disk_total_bytes', 'Total disk space in bytes', ['mountpoint'])
DISK_IO_READ = Counter('disk_io_read_bytes', 'Disk I/O read in bytes')
DISK_IO_WRITE = Counter('disk_io_write_bytes', 'Disk I/O write in bytes')

# Метрики сети
NETWORK_BYTES_SENT = Counter('network_bytes_sent', 'Network bytes sent', ['interface'])
NETWORK_BYTES_RECV = Counter('network_bytes_recv', 'Network bytes received', ['interface'])
NETWORK_PACKETS_SENT = Counter('network_packets_sent', 'Network packets sent', ['interface'])
NETWORK_PACKETS_RECV = Counter('network_packets_recv', 'Network packets received', ['interface'])

# Метрики процесса
PROCESS_THREADS = Gauge('process_threads_total', 'Total number of threads')
PROCESS_OPEN_FILES = Gauge('process_open_files', 'Number of open files')
PROCESS_CONNECTIONS = Gauge('process_connections', 'Number of network connections')

app = Flask(__name__)

def collect_system_metrics():
    """Собирает системные метрики"""
    try:
        # CPU метрики
        cpu_times_percent = psutil.cpu_times_percent()
        CPU_USAGE.set(psutil.cpu_percent(interval=None))
        CPU_SYSTEM.set(cpu_times_percent.system)
        CPU_USER.set(cpu_times_percent.user)
        CPU_CORES.set(psutil.cpu_count())

        # Метрики памяти
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        MEMORY_USAGE.set(memory.used)
        MEMORY_TOTAL.set(memory.total)
        MEMORY_AVAILABLE.set(memory.available)
        MEMORY_CACHED.set(memory.cached)
        MEMORY_SWAP_USED.set(swap.used)
        MEMORY_SWAP_TOTAL.set(swap.total)

        # Метрики диска
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                DISK_USAGE.labels(mountpoint=partition.mountpoint).set(usage.used)
                DISK_TOTAL.labels(mountpoint=partition.mountpoint).set(usage.total)
            except:
                continue

        # Метрики I/O
        disk_io = psutil.disk_io_counters()
        DISK_IO_READ._value.set(disk_io.read_bytes)
        DISK_IO_WRITE._value.set(disk_io.write_bytes)

        # Метрики сети
        network = psutil.net_io_counters(pernic=True)
        for interface, counters in network.items():
            NETWORK_BYTES_SENT.labels(interface=interface)._value.set(counters.bytes_sent)
            NETWORK_BYTES_RECV.labels(interface=interface)._value.set(counters.bytes_recv)
            NETWORK_PACKETS_SENT.labels(interface=interface)._value.set(counters.packets_sent)
            NETWORK_PACKETS_RECV.labels(interface=interface)._value.set(counters.packets_recv)

        # Метрики процесса
        process = psutil.Process()
        PROCESS_THREADS.set(process.num_threads())
        PROCESS_OPEN_FILES.set(len(process.open_files()))
        PROCESS_CONNECTIONS.set(len(process.connections()))

    except Exception as e:
        logging.error(f"Error collecting metrics: {str(e)}")

@app.before_request
def before_request():
    ACTIVE_REQUESTS.inc()
    request.start_time = time.time()

@app.after_request
def after_request(response):
    ACTIVE_REQUESTS.dec()
    resp_time = time.time() - request.start_time
    REQUEST_LATENCY.labels(endpoint=request.endpoint).observe(resp_time)
    REQUEST_COUNT.labels(method=request.method, endpoint=request.endpoint).inc()
    return response

@app.route('/')
def home():
    try:
        hostname = socket.gethostname()
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return render_template('index.html',
                             hostname=hostname,
                             current_time=current_time)
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
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
    collect_system_metrics()
    return generate_latest()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(host='0.0.0.0', port=5000)