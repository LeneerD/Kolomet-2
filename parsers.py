import random
import re
from config import CONSTANTS

# ---- Скомпилированные регулярные выражения ----
RE_MODS = re.compile(r'([+-]\d+)')
RE_EXPLODE = re.compile(r'(!{1,2})(\d*)')
RE_MULT = re.compile(r'[x*](\d+)')

def explode_dice(initial_value, dice_type, explode_type):
    total = initial_value
    current = initial_value
    while True:
        if explode_type == '!':
            if current == dice_type:
                new_roll = random.randint(1, dice_type)
                total += new_roll
                current = new_roll
            else:
                break
        elif explode_type == '!!':
            if current == dice_type or current == 1:
                new_roll = random.randint(1, dice_type)
                if current == dice_type:
                    total += new_roll
                else:
                    total -= new_roll
                current = new_roll
            else:
                break
    return total

def parse_single_component(comp):
    comp = comp.strip()
    if not comp:
        return None, "Пустой компонент", None

    comp = comp.replace('к', 'd').replace('К', 'd').replace('д', 'd').replace('Д', 'd')

    adv_dis_map = {
        'adv': 1, 'advantage': 1, 'пр': 1, 'преимущество': 1,
        'dis': -1, 'disadvantage': -1, 'пом': -1, 'помеха': -1
    }
    for kw in adv_dis_map:
        if comp.lower().startswith(kw):
            rest = comp[len(kw):]
            roll1, roll2 = random.randint(1, 20), random.randint(1, 20)
            result = max(roll1, roll2) if adv_dis_map[kw] == 1 else min(roll1, roll2)
            mods = RE_MODS.findall(rest)
            for mod in mods:
                result += int(mod)
            # Формируем детали: показываем оба кубика и модификаторы
            details = f"{roll1}, {roll2}"
            if mods:
                details += " " + " ".join(mods)
            return result, None, details

    if 'd' not in comp:
        try:
            return int(comp), None, None
        except ValueError:
            return None, f"Не удалось распознать '{comp}'. Пример: 2d6+3", None

    explode_match = RE_EXPLODE.search(comp)
    if explode_match:
        explode_type = explode_match.group(1)
        explode_count_str = explode_match.group(2)
        explode_count = int(explode_count_str) if explode_count_str else 1
        comp = comp[:explode_match.start()] + comp[explode_match.end():]
    else:
        explode_type = None
        explode_count = 0

    resist = False
    if comp.endswith('r') or comp.endswith('с'):
        resist = True
        comp = comp[:-1]

    multiplier = 1
    mult_match = RE_MULT.search(comp)
    if mult_match:
        multiplier = int(mult_match.group(1))
        comp = comp[:mult_match.start()] + comp[mult_match.end():]

    mods = RE_MODS.findall(comp)
    for mod in mods:
        comp = comp.replace(mod, '')

    if 'd' not in comp:
        return None, "Отсутствует 'd' в компоненте", None

    parts = comp.split('d')
    if parts[0] == '':
        num_dice = 1
    else:
        try:
            num_dice = int(parts[0])
        except ValueError:
            return None, f"Количество кубиков должно быть числом, например 2d6", None

    dice_type_str = parts[1]
    if dice_type_str == '%':
        dice_type = 100
    else:
        try:
            dice_type = int(dice_type_str)
        except ValueError:
            return None, f"Тип кубика должен быть числом, например d20 или d6", None

    if num_dice > CONSTANTS["max_dice"] or dice_type > CONSTANTS["max_dice_type"] or num_dice <= 0 or dice_type <= 0:
        return None, f"Слишком много кубиков (макс. {CONSTANTS['max_dice']}) или слишком большой кубик (макс. d{CONSTANTS['max_dice_type']})", None

    rolls = [random.randint(1, dice_type) for _ in range(num_dice)]
    if explode_type:
        if explode_count > num_dice:
            explode_count = num_dice
        indices = random.sample(range(num_dice), explode_count) if explode_count > 0 else []
        total = 0
        for i, val in enumerate(rolls):
            if i in indices:
                total += explode_dice(val, dice_type, explode_type)
            else:
                total += val
    else:
        total = sum(rolls)

    for mod in mods:
        total += int(mod)
    total *= multiplier
    if resist:
        total //= 2

    details_parts = []
    if len(rolls) > 1:
        details_parts.append(", ".join(map(str, rolls)))
    else:
        details_parts.append(str(rolls[0]))
    if mods:
        details_parts.append(" ".join(mods))
    if multiplier != 1:
        details_parts.append(f"x{multiplier}")
    if resist:
        details_parts.append("/2")
    details = " ".join(details_parts)

    return total, None, details

def parse_expression(expr):
    if not expr:
        return None, "Пустое выражение", None
    parts = re.split(r'\s+', expr)
    total = 0
    all_details = []
    for part in parts:
        if not part:
            continue
        sign = 1
        if part.startswith('+'):
            sign = 1
            part = part[1:]
        elif part.startswith('-'):
            sign = -1
            part = part[1:]
        if not part:
            continue
        value, error, detail = parse_single_component(part)
        if error:
            return None, error, None
        total += sign * value
        if detail:
            all_details.append(f"{sign if sign == -1 else ''}{detail}")
    return total, None, " ; ".join(all_details) if all_details else None