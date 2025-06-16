import subprocess
import time
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def start_api():
    try:
        logger.info("Запуск API сервера...")
        api_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "api.fastapi_main:app",
             "--host", "127.0.0.1", "--port", "8000"],
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(2)  # Даем серверу время на запуск
        logger.info("API сервер запущен")
        return api_process
    except Exception as e:
        logger.error(f"Ошибка запуска API: {e}")
        return None
