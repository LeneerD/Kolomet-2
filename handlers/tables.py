import random
import re
from handlers.basic import get_tables, roll_table, roll_spark, roll_exploration
from utils import format_response
from config import CONSTANTS

def handle_spark(mention, args, comment):
    if args:
        try:
            num = int(args[0])
        except ValueError:
            return "Ошибка: укажите число. Пример: /spark 42", None, None
        roll, result = roll_spark(num)
    else:
        roll, result = roll_spark()
    if roll is None:
        return f"Ошибка: {result}", None, None
    spark = get_tables().get("spark", {})
    max_key = max(map(int, spark.keys())) if spark else 0
    return f"Бросок d{max_key}: {roll} — {result}", None, None

def handle_skill(mention, args, comment):
    table_name = args[0] if args else 'melee'
    result, error, _ = roll_table(table_name)
    if error:
        return f"Ошибка: {error}", None, None
    return f"Бросок навыка ({table_name}): {result}", None, None

def handle_table(mention, args, comment):
    if not args:
        tables = get_tables().get("tables", {})
        available = ", ".join(tables.keys()) if tables else "нет загруженных таблиц"
        return f"Укажите имя таблицы. Доступные: {available}", None, None
    table_name = args[0]
    result, error, _ = roll_table(table_name)
    if error:
        return f"Ошибка: {error}", None, None
    return f"Бросок по таблице {table_name}: {result}", None, None

def handle_tables(mention, args, comment):
    tables = get_tables().get("tables", {})
    if tables:
        return f"Доступные таблицы: {', '.join(tables.keys())}", None, None
    return "Таблицы навыков не загружены. Проверьте файл tables.json.", None, None

def handle_exp(mention, args, comment):
    if not args:
        return "Укажите категорию: common, rare или legendary. Пример: /exp common 3d6 или /exp common 10", None, None
    category = args[0].lower()
    if category not in ('common', 'rare', 'legendary'):
        return f"Неверная категория. Доступные: common, rare, legendary.", None, None

    if len(args) == 1:
        result, error, _ = roll_exploration(category, num_dice=CONSTANTS["default_exploration_dice"])
        if error:
            return f"Ошибка: {error}", None, None
        return result, None, None

    expr = args[1].lower().replace(' ', '')
    if expr.isdigit():
        try:
            direct_val = int(expr)
            if direct_val < 0:
                raise ValueError
            result, error, _ = roll_exploration(category, direct_value=direct_val)
            if error:
                return f"Ошибка: {error}", None, None
            return result, None, None
        except ValueError:
            return "Ошибка: укажите положительное целое число.", None, None

    if 'd' not in expr:
        return "Ошибка: укажите выражение с d (например, 3d6) или простое число.", None, None

    num_dice = CONSTANTS["default_exploration_dice"]
    modifier = 0
    mod_match = re.search(r'([+-]\d+)$', expr)
    if mod_match:
        modifier = int(mod_match.group(1))
        expr = expr[:mod_match.start()]
    if 'd' in expr:
        parts = expr.split('d')
        if parts[0] == '':
            num_dice = 1
        else:
            try:
                num_dice = int(parts[0])
                if num_dice < 1:
                    raise ValueError
            except ValueError:
                return "Ошибка: некорректное число кубиков. Пример: 3d6 или 11+d6.", None, None
    else:
        return "Ошибка: выражение должно содержать d. Пример: 3d6 или 11+d6.", None, None

    result, error, _ = roll_exploration(category, num_dice, modifier)
    if error:
        return f"Ошибка: {error}", None, None
    return result, None, None