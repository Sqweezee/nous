import time
import requests
import logging
import random
import re
from itertools import cycle

# Пути к файлам
API_KEYS_FILE = "api_keys.txt"
QUESTIONS_FILE = "questions.txt"

# Hyperbolic API
HYPERBOLIC_API_URL = "https://inference-api.nousresearch.com/v1/chat/completions"

# Настройки генерации
MAX_TOKENS = 4096
TEMPERATURE = 0.7
TOP_P = 0.9

# Диапазон задержки между запросами
MIN_DELAY = 280
MAX_DELAY = 580

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# 📦 Список моделей
MODELS = [
    "Hermes-4-70B",
    "Hermes-4-405B",
]

# 🔄 Циклический перебор моделей
model_cycle = cycle(MODELS)

# 🔐 Загрузка API-ключей
def load_api_keys(filename: str) -> list:
    try:
        with open(filename, "r", encoding="utf-8") as f:
            keys = [line.strip() for line in f if line.strip()]
        if not keys:
            raise ValueError("Файл API-ключей пуст.")
        return keys
    except Exception as e:
        logger.error(f"Ошибка загрузки API-ключей из {filename}: {e}")
        return []

# ✅ Загружаем ключи
api_keys = load_api_keys(API_KEYS_FILE)

if not api_keys:
    logger.error("❌ Не загружены API-ключи! Проверьте файл api_keys.txt")
    exit(1)

# 🔄 Цикл по API-ключам
api_cycle = cycle(enumerate(api_keys, 1))

# 📤 Отправка запроса с заданной моделью
def send_request(question: str, model: str) -> bool:
    api_index, api_key = next(api_cycle)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "messages": [{"role": "user", "content": question}],
        "model": model,
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE,
        "top_p": TOP_P
    }

    logger.info(f"➡️  Используется API-ключ #{api_index}, модель: {model}")

    try:
        response = requests.post(HYPERBOLIC_API_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        response_json = response.json()
        answer = response_json.get("choices", [{}])[0].get("message", {}).get("content", "")

        logger.info("✅ Ответ успешно получен")
        logger.info(f"📥 Ответ: {answer.strip()}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Ошибка при запросе: {e}")
        return False

# 📁 Основной цикл
def main():
    try:
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
            questions = [line.strip() for line in f if line.strip()]
    except Exception as e:
        logger.error(f"Ошибка чтения файла {QUESTIONS_FILE}: {e}")
        return

    if not questions:
        logger.error(f"⚠️ В файле {QUESTIONS_FILE} нет вопросов.")
        return

    index = 0
    while True:
        question = questions[index]
        model = next(model_cycle)

        logger.info(f"📌 Вопрос #{index + 1}: {question}")

        send_request(question, model)

        index = (index + 1) % len(questions)

        delay = random.uniform(MIN_DELAY, MAX_DELAY)
        logger.info(f"⏳ Ожидание {delay:.1f} секунд до следующего вопроса...")
        time.sleep(delay)

# 🚀 Запуск
if __name__ == "__main__":
    main()

