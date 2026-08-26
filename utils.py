import logging
import json
from config import OWNER_ID, TESTERS_FILE
from vk_utils import vk

logger = logging.getLogger(__name__)

donor_cache = {}
_testers = []  # кешированный список

def load_testers():
    global _testers
    try:
        with open(TESTERS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            _testers = data.get("testers", [])
    except (FileNotFoundError, json.JSONDecodeError, IOError):
        _testers = []
    return _testers

def reload_testers():
    return load_testers()

# Загружаем при старте
load_testers()

def is_donor(user_id):
    if OWNER_ID is not None and user_id == OWNER_ID:
        return True

    if user_id in _testers:
        return True

    user_id_str = str(user_id)
    if user_id_str in donor_cache:
        return donor_cache[user_id_str]
    try:
        response = vk.method('donut.isDon', {'user_id': user_id})
        donor_cache[user_id_str] = response
        return response
    except Exception as e:
        logger.error(f"Ошибка проверки доната для {user_id}: {e}")
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