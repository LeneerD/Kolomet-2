import random
from utils import is_donor, format_response
from handlers.basic import get_tables, roll_spark, roll_exploration

def handle_donate_roll(mention, args, comment, user_id):
    if not is_donor(user_id):
        return "Этот функционал доступен только донатерам! Оформите подписку VK Donut.", None, None
    rolls = [random.randint(1, 6) for _ in range(4)]
    total = sum(rolls)
    return f"Эксклюзивный бросок 4d6: {total}", ", ".join(map(str, rolls)), None

def handle_donate_stats(mention, args, comment, user_id):
    if not is_donor(user_id):
        return "Этот функционал доступен только донатерам! Оформите подписку VK Donut.", None, None
    stats = []
    for _ in range(7):
        rolls = [random.randint(1, 6) for _ in range(4)]
        rolls.sort()
        stats.append(sum(rolls[1:]))
    return f"Эксклюзивные характеристики (7 шт): {', '.join(map(str, stats))}", None, None

def handle_donate_spark(mention, args, comment, user_id):
    if not is_donor(user_id):
        return "Этот функционал доступен только донатерам! Оформите подписку VK Donut.", None, None
    spark = get_tables().get("spark", {})
    if not spark:
        return "Таблица Spark не загружена.", None, None
    max_key = max(map(int, spark.keys())) if spark else 0
    if args:
        try:
            num = int(args[0])
        except ValueError:
            return "Ошибка: укажите число. Пример: /donate_spark 42", None, None
        if str(num) in spark:
            return f"Прокачка Spark #{num}: {spark[str(num)]}", None, None
        else:
            return f"Запись {num} не найдена.", None, None
    else:
        roll = random.randint(1, max_key)
        modified = min(roll + 5, max_key)
        desc = spark.get(str(modified), "Описание отсутствует")
        return f"Эксклюзивный бросок d{max_key} с бонусом +5: {modified} (исходный бросок: {roll}) — {desc}", None, None