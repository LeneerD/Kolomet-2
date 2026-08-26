import json
import logging
import random
import time
import vk_api
from config import GROUP_ID, NICKNAMES_FILE

logger = logging.getLogger(__name__)

vk = None
longpoll = None
nicknames = {}
user_cache = {}  # user_id -> (timestamp, name)
CACHE_TTL = 3600  # 1 час

def init_vk(token):
    global vk, longpoll
    session = vk_api.VkApi(token=token)
    vk = session.get_api()
    longpoll = vk_api.bot_longpoll.VkBotLongPoll(session, GROUP_ID)
    return session

def load_nicknames():
    try:
        with open(NICKNAMES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, IOError):
        return {}

def save_nicknames(data):
    try:
        with open(NICKNAMES_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except IOError as e:
        logger.error(f"Ошибка сохранения nicknames.json: {e}")

def reload_nicknames():
    global nicknames
    nicknames = load_nicknames()
    # Очищаем кеш, чтобы при следующем запросе использовались новые имена
    user_cache.clear()
    return nicknames

def get_user_name(user_id):
    global nicknames
    user_id_str = str(user_id)
    # 1. Кастомное имя из nicknames.json
    if user_id_str in nicknames:
        return nicknames[user_id_str]

    # 2. Проверяем кеш с TTL
    now = time.time()
    if user_id in user_cache:
        timestamp, name = user_cache[user_id]
        if now - timestamp < CACHE_TTL:
            return name

    # 3. Запрос к VK API
    try:
        user = vk.users.get(user_ids=user_id, fields=[])[0]
        name = user['first_name']
    except Exception as e:
        logger.error(f"Ошибка получения имени для {user_id}: {e}")
        name = f"Пользователь {user_id}"

    # Сохраняем в кеш
    user_cache[user_id] = (now, name)
    return name

def mention_user(user_id, peer_id):
    if peer_id != user_id:
        return f"[id{user_id}|{get_user_name(user_id)}], "
    return ""

def send_message(user_id, message, peer_id=None):
    try:
        vk.messages.send(
            user_id=user_id if peer_id is None else None,
            peer_id=peer_id,
            message=message,
            random_id=random.randint(1, 2**31)
        )
    except Exception as e:
        logger.error(f"Ошибка отправки: {e}")

# Загружаем никнеймы при старте
nicknames = load_nicknames()