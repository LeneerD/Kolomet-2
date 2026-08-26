import os
import sys
import time
import logging
from requests.exceptions import ReadTimeout, ConnectionError
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

sys.path.insert(0, os.path.dirname(__file__))

import config
from db import init_db
from tables_loader import load_all_tables
from vk_utils import init_vk, longpoll, vk, send_message, mention_user, reload_nicknames
from utils import format_response, extract_comment, reload_testers
from handlers.basic import set_tables, handle_help, handle_coin, handle_rand, handle_stats, handle_dpercent, handle_adv, handle_dis, handle_ping, handle_inj, handle_d66
from handlers.tables import handle_spark, handle_skill, handle_table, handle_tables, handle_exp
from handlers.donate import handle_donate_roll, handle_donate_stats, handle_donate_spark
from handlers.premium import handle_alias, handle_character, handle_monster
from parsers import parse_expression
from db import get_alias

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_longpoll_with_retry(session, group_id, retries=5, delay=3):
    for attempt in range(1, retries + 1):
        try:
            longpoll = VkBotLongPoll(session, group_id)
            logger.info(f"LongPoll успешно инициализирован (попытка {attempt})")
            return longpoll
        except Exception as e:
            logger.warning(f"Ошибка инициализации LongPoll (попытка {attempt}/{retries}): {e}")
            if attempt == retries:
                raise
            time.sleep(delay)

session = init_vk(config.VK_TOKEN)
longpoll = init_longpoll_with_retry(session, config.GROUP_ID)

init_db()

tables_data = load_all_tables()
set_tables(tables_data)

logger.info("Бот успешно запущен и слушает сообщения...")

# ---- Функции перезагрузки ----
def handle_reload(mention, args, comment, user_id):
    if config.OWNER_ID is None:
        return "Команда /reload отключена (не задан OWNER_ID).", None, None
    if user_id != config.OWNER_ID:
        return "У вас нет прав на использование /reload.", None, None

    results = []
    new_tables = load_all_tables()
    if new_tables:
        set_tables(new_tables)
        results.append("✅ Таблицы обновлены")
    else:
        results.append("❌ Таблицы не обновлены (ошибка загрузки)")

    reload_testers()
    results.append("✅ Список тестировщиков обновлён")

    reload_nicknames()
    results.append("✅ Кастомные имена обновлены")

    return "\n".join(results), None, None

def handle_reload_testers(mention, args, comment, user_id):
    if config.OWNER_ID is None:
        return "Команда /reload_testers отключена (не задан OWNER_ID).", None, None
    if user_id != config.OWNER_ID:
        return "У вас нет прав на использование /reload_testers.", None, None
    reload_testers()
    return "Список тестировщиков успешно перезагружен из файла.", None, None

# ---- Словарь команд ----
COMMAND_HANDLERS = {
    "help": handle_help,
    "помощь": handle_help,
    "coin": handle_coin,
    "монетка": handle_coin,
    "rand": handle_rand,
    "random": handle_rand,
    "s": handle_stats,
    "scores": handle_stats,
    "х": handle_stats,
    "характеристики": handle_stats,
    "d%": handle_dpercent,
    "к%": handle_dpercent,
    "adv": handle_adv,
    "advantage": handle_adv,
    "пр": handle_adv,
    "преимущество": handle_adv,
    "dis": handle_dis,
    "disadvantage": handle_dis,
    "пом": handle_dis,
    "помеха": handle_dis,
    "ping": handle_ping,
    "inj": handle_inj,
    "ранение": handle_inj,
    "injury": handle_inj,
    "d66": handle_d66,
    "spark": handle_spark,
    "skill": handle_skill,
    "навык": handle_skill,
    "table": handle_table,
    "tables": handle_tables,
    "exp": handle_exp,
    "donate_roll": handle_donate_roll,
    "донат_бросок": handle_donate_roll,
    "donate_stats": handle_donate_stats,
    "донат_статы": handle_donate_stats,
    "donate_spark": handle_donate_spark,
    "донат_искра": handle_donate_spark,
    "al": handle_alias,
    "ал": handle_alias,
    "char": handle_character,
    "перс": handle_character,
    "character": handle_character,
    "mon": handle_monster,
    "мон": handle_monster,
    "monster": handle_monster,
    "reload": handle_reload,
    "reload_testers": handle_reload_testers,
    "обновить_тестеров": handle_reload_testers,
}

# ---- Команды, требующие user_id ----
REQUIRES_USER_ID = {
    "reload", "reload_testers", "обновить_тестеров",
    "donate_roll", "донат_бросок", "donate_stats", "донат_статы",
    "donate_spark", "донат_искра", "al", "ал", "char", "перс",
    "character", "mon", "мон", "monster"
}

# ---- Главный цикл ----
while True:
    try:
        for event in longpoll.listen():
            try:
                if event.type != VkBotEventType.MESSAGE_NEW:
                    continue
                if not event.object or not event.object.message:
                    continue

                peer_id = event.object.message.get('peer_id')
                user_id = event.object.message.get('from_id')
                text = event.object.message.get('text')
                if not text:
                    continue

                text = text.strip()
                if not text.startswith('/'):
                    continue

                cmd_raw = text[1:].strip()
                if not cmd_raw:
                    send_message(user_id, format_response(mention_user(user_id, peer_id), "Введите команду. Например: /d20"), peer_id)
                    continue

                cmd_clean, comment = extract_comment(cmd_raw)
                parts = cmd_clean.split()
                if not parts:
                    send_message(user_id, format_response(mention_user(user_id, peer_id), "Введите команду. Например: /d20"), peer_id)
                    continue

                command = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []
                mention = mention_user(user_id, peer_id)

                # Проверка на алиас
                if command not in COMMAND_HANDLERS:
                    alias_cmd = get_alias(user_id, command)
                    if alias_cmd:
                        result, error, details = parse_expression(alias_cmd)
                        if error:
                            send_message(user_id, format_response(mention, f"Ошибка в алиасе: {error}", None, comment), peer_id)
                        else:
                            main = f"алиас '{command}' → {alias_cmd}: {result}"
                            send_message(user_id, format_response(mention, main, details, comment), peer_id)
                        continue

                if command in COMMAND_HANDLERS:
                    handler = COMMAND_HANDLERS[command]
                    if command in REQUIRES_USER_ID:
                        main, details, _ = handler(mention, args, comment, user_id)
                    else:
                        main, details, _ = handler(mention, args, comment)
                    send_message(user_id, format_response(mention, main, details, comment), peer_id)
                else:
                    result, error, details = parse_expression(cmd_clean)
                    if error:
                        send_message(user_id, format_response(mention, f"Ошибка: {error}", None, comment), peer_id)
                    else:
                        main = f"бросок {cmd_clean}: {result}"
                        send_message(user_id, format_response(mention, main, details, comment), peer_id)

            except Exception as e:
                logger.error(f"Ошибка обработки события: {e}")
                continue

    except (ReadTimeout, ConnectionError, Exception) as e:
        logger.error(f"Ошибка соединения с VK: {e}. Переподключение через 5 секунд...")
        time.sleep(5)
        session = init_vk(config.VK_TOKEN)
        longpoll = init_longpoll_with_retry(session, config.GROUP_ID)