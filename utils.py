import logging
import json
import time
import config
from vk_utils import vk

logger = logging.getLogger(__name__)

donor_cache = {}  # user_id_str -> (timestamp, is_donor)
_testers = []     # кешированный список тестеров
CACHE_TTL = 3600  # 1 час

def load_testers():
    global _testers
    try:
        with open(config.TESTERS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            _testers = data.get("testers", [])
    except (FileNotFoundError, json.JSONDecodeError, IOError):
        _testers = []
    return _testers

def reload_testers():
    return load_testers()

load_testers()

def is_donor(user_id):
    # 1. Владелец всегда донатер
    if config.OWNER_ID is not None and user_id == config.OWNER_ID:
        return True

    # 2. Тестировщики
    if user_id in _testers:
        return True

    # 3. Проверяем кеш с TTL
    user_id_str = str(user_id)
    now = time.time()
    if user_id_str in donor_cache:
        timestamp, result = donor_cache[user_id_str]
        if now - timestamp < CACHE_TTL:
            return result

    # 4. Запрос к VK Donut API
    try:
        response = vk.method('donut.isDon', {'user_id': user_id})
        donor_cache[user_id_str] = (now, response)
        return response
    except Exception as e:
        logger.error(f"Ошибка проверки доната для {user_id}: {e}")
        donor_cache[user_id_str] = (now, False)
        return False

def premium_only(func):
    def wrapper(mention, args, comment, user_id):
        if not is_donor(user_id):
            return "Эта функция доступна только донатерам! Оформите подписку VK Donut.", None, None
        return func(mention, args, comment, user_id)
    return wrapper

def format_response(mention, main, details=None, comment=None):
    if details:
        parts = f"{main} ({details})"
    else:
        parts = main
    if comment:
        parts += f" 💬 {comment}"
    return f"{mention}{parts}"

def extract_comment(cmd):
    if '#' in cmd:
        clean, comment = cmd.rsplit('#', 1)
        return clean.strip(), comment.strip()
    return cmd, None

def generate_stats():
    import random
    stats = []
    for _ in range(6):
        rolls = [random.randint(1, 6) for _ in range(4)]
        rolls.sort()
        stats.append(sum(rolls[1:]))
    return stats

def flip_coin():
    import random
    return "Орёл!" if random.choice([True, False]) else "Решка!"

def random_number(args):
    import random
    if not args:
        return random.randint(0, 100), None
    if len(args) == 2:
        try:
            a, b = sorted(map(int, args[:2]))
            return random.randint(a, b), None
        except ValueError:
            return None, "Введите два целых числа. Пример: /rand 1 100"
    return None, "Укажите два числа через пробел. Пример: /rand 1 100"