import random
from parsers import parse_expression
from utils import format_response, generate_stats, flip_coin, random_number
from vk_utils import send_message

tables_data = {}

def set_tables(data):
    global tables_data
    tables_data = data

def get_tables():
    return tables_data

def get_table(table_name):
    if table_name not in tables_data.get("tables", {}):
        return None
    return tables_data["tables"][table_name]

# ---- Базовые броски ----
def roll_table(table_name):
    tables = tables_data.get("tables", {})
    if not tables:
        return None, "Таблицы навыков не загружены.", None
    if table_name not in tables:
        return None, f"Таблица '{table_name}' не найдена. Доступны: {', '.join(tables.keys())}", None

    roll1, roll2 = random.randint(1, 6), random.randint(1, 6)
    total = roll1 + roll2
    entry = tables[table_name].get(str(total))
    if not entry:
        return None, f"Для суммы {total} нет записи в таблице.", None

    name, desc = entry if isinstance(entry, list) and len(entry) >= 2 else (entry, "")
    result = f"2d6 → {roll1}+{roll2} = {total} — {name} — {desc}"
    return result, None, None

def roll_spark(number=None):
    spark = tables_data.get("spark", {})
    if not spark:
        return None, "Таблица Spark не загружена.", None
    if number is not None:
        key = str(number)
        if key in spark:
            return number, spark[key], None
        else:
            return None, f"Запись {number} не найдена", None
    max_key = tables_data.get("spark_max_key", 0)
    roll = random.randint(1, max_key) if max_key else 0
    return roll, spark.get(str(roll), "Описание отсутствует"), None

def roll_exploration(category, num_dice=None, modifier=0, direct_value=None):
    exp_tables = tables_data.get("exploration_tables", {})
    if category not in exp_tables:
        return None, f"Неизвестная категория '{category}'. Доступны: common, rare, legendary", None
    table = exp_tables[category]
    if not table:
        return None, f"Таблица '{category}' не загружена.", None

    if direct_value is not None:
        total = direct_value
        desc = table.get(str(total))
        result = f"Значение {total} из таблицы {category.capitalize()}\nДукаты: {total * 10}"
        if desc:
            result += f"\nОписание: {desc}"
        return result, None, None

    if num_dice is None:
        num_dice = 3
    rolls = [random.randint(1, 6) for _ in range(max(1, num_dice))]
    total = sum(rolls) + modifier
    desc = table.get(str(total))
    result = f"Бросок {len(rolls)}d6: {', '.join(map(str, rolls))}"
    if modifier:
        result += f" {modifier:+d}"
    result += f" = {total}\nДукаты: {total * 10}"
    if desc:
        result += f"\nОписание: {desc}"
    return result, None, None

def roll_injury():
    injury_table = tables_data.get("injury", {})
    if not injury_table:
        return None, "Таблица ранений не загружена.", None, None, None
    units, tens = random.randint(1, 6), random.randint(1, 6)
    result = tens * 10 + units
    entry = injury_table.get(str(result), ["Unknown", "No description"])
    return result, units, tens, entry[0], entry[1]

def roll_d66():
    tens = random.randint(1, 6)
    units = random.randint(1, 6)
    result = tens * 10 + units
    return result, tens, units

# ---- Обработчики команд ----
def handle_help(mention, args, comment):
    help_text = (
        "🎲 *Команды бота:*\n\n"
        "*Бросок кубиков* (можно через /):\n"
        "/d20 или /к20 — бросить 20-гранный кубик\n"
        "/2d6+1d20+5 — несколько кубиков разных типов\n"
        "/d100-3 или /к100-3 — d100 с модификатором\n"
        "/d66 — бросок D66 (две шестёрки, первая – десятки, вторая – единицы)\n"
        "/d% или /к% — бросок процентной кости (1-100)\n\n"
        "*Расширенные броски:*\n"
        "/<выражение> — поддерживает:\n"
        "  - множители: x{N} или *{N} (например, /4d8-3x10)\n"
        "  - резист: r или с в конце (деление на 2, округление вниз)\n"
        "  - взрывные: ! или !! с количеством костей (например, /6d6!2)\n"
        "  - преимущество/помеха: /adv или /dis (или русские /пр, /пом)\n"
        "  - комбинирование через пробел или +/-\n"
        "  - пример: /4d8-3x10r -2d6+4 d% 6d6!!2\n\n"
        "*Специальные команды:*\n"
        "/s или /scores или /х, /характеристики — генерация шести характеристик (4d6, сумма трёх наибольших)\n"
        "/coin или /монетка — подбросить монетку\n"
        "/rand 1 100 — случайное число в диапазоне\n"
        "/inj или /ранение — бросок на ранение по таблице Elites Injury Chart (D66)\n"
        "/spark [номер] — показать описание прокачки Spark (если номер не указан — случайный бросок)\n"
        "/skill [таблица] — бросок 2d6 по таблице прокачки Trench Crusade (по умолчанию melee)\n"
        "/table <таблица> — бросок по указанной таблице\n"
        "/tables — список доступных таблиц\n"
        "/exp <common|rare|legendary> [Xd6 или число+d6 или просто число] — бросок по таблице Exploration (по умолчанию 3d6). Если указать просто число, выводится описание для этого числа.\n"
        "/ping — проверка работы\n"
        "/reload — перезагрузить таблицы (только для владельца)\n"
        "/help — эта справка\n\n"
        "*Премиум-функции (только для донатеров VK Donut):*\n"
        "/ал {имя} {команда} — сохранить алиас (например, /ал 2атаки 2к6+3)\n"
        "/ал — посмотреть список алиасов\n"
        "/ал уд {имя} — удалить алиас\n"
        "/char {имя} — создать персонажа или переключиться на него\n"
        "/char — посмотреть список персонажей\n"
        "/char del {имя} — удалить персонажа\n"
        "/char set {параметр}={значение} — задать параметр персонажу\n"
        "/char stats — посмотреть параметры активного персонажа\n"
        "/char hp {±N} — изменить хиты активного персонажа\n"
        "/char +lvl — повысить уровень активного персонажа\n"
        "/mon {имя} — создать монстра\n"
        "/mon — посмотреть список монстров\n"
        "/mon set {параметр}={значение} — задать параметр монстру\n"
        "/mon stats — посмотреть параметры активного монстра\n"
        "*Комментарии:*\nДобавьте `# текст` в конце команды для пояснения."
    )
    return help_text, None, None

def handle_coin(mention, args, comment):
    return f"Бросок монетки: {flip_coin()}", None, None

def handle_rand(mention, args, comment):
    result, error = random_number(args)
    if error:
        return f"Ошибка: {error}", None, None
    return f"Случайное число: {result}", None, None

def handle_stats(mention, args, comment):
    stats = generate_stats()
    return f"Характеристики: {', '.join(map(str, stats))}", None, None

def handle_dpercent(mention, args, comment):
    result, error, details = parse_expression("d%")
    if error:
        return f"Ошибка: {error}", None, None
    return f"Бросок процентной кости: {result}", details, None

def handle_adv(mention, args, comment):
    expr = ' '.join(args) if args else ''
    full_expr = f"adv {expr}" if expr else "adv"
    result, error, details = parse_expression(full_expr)
    if error:
        return f"Ошибка: {error}", None, None
    return f"Бросок с преимуществом: {result}", details, None

def handle_dis(mention, args, comment):
    expr = ' '.join(args) if args else ''
    full_expr = f"dis {expr}" if expr else "dis"
    result, error, details = parse_expression(full_expr)
    if error:
        return f"Ошибка: {error}", None, None
    return f"Бросок с помехой: {result}", details, None

def handle_ping(mention, args, comment):
    return "Pong! Бот работает.", None, None

def handle_inj(mention, args, comment):
    result, units, tens, name, desc = roll_injury()
    if result is None:
        return f"Ошибка: {desc}", None, None
    return f"Бросок на ранение: {tens}+{units} = **{result}** — *{name}* — {desc}", None, None

def handle_d66(mention, args, comment):
    result, tens, units = roll_d66()
    return f"Бросок D66: **{result}** (десятки: {tens}, единицы: {units})", None, None