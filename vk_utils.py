import json
import logging
import random
import vk_api
from config import GROUP_ID, NICKNAMES_FILE

logger = logging.getLogger(__name__)

vk = None
longpoll = None
nicknames = {}
user_cache = {}

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
    """Перезагружает кастомные имена из файла."""
    global nicknames
    nicknames = load_nicknames()
    return nicknames

def get_user_name(user_id):
    global nicknames
    user_id_str = str(user_id)
    if user_id_str in nicknames:
        return nicknames[user_id_str]
    if user_id not in user_cache:
        try:
            user = vk.users.get(user_ids=user_id, fields=[])[0]
            user_cache[user_id] = user['first_name']
        except:
            user_cache[user_id] = f"Пользователь {user_id}"
    return user_cache[user_id]

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

nicknames = load_nicknames()