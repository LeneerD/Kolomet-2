from db import (
    save_alias, get_alias, get_user_aliases, delete_alias,
    create_character, delete_character, get_user_characters,
    set_character_stat, get_character_stat, get_all_character_stats,
    set_active_character, get_active_character,
    create_monster, delete_monster, get_user_monsters,
    set_monster_stat, get_monster_stat, get_all_monster_stats,
    set_active_monster, get_active_monster
)
from utils import premium_only, format_response

# ---- Алиасы ----
@premium_only
def handle_alias(mention, args, comment, user_id):
    if not args:
        aliases = get_user_aliases(user_id)
        if not aliases:
            return "У вас нет сохранённых алиасов.", None, None
        lines = ["*Ваши алиасы:*"]
        for name, cmd in aliases:
            lines.append(f"/{name} → {cmd}")
        return "\n".join(lines), None, None

    if args[0] in ("del", "delete", "уд", "удалить"):
        if len(args) < 2:
            return "Укажите имя алиаса для удаления. Пример: /ал уд 2атаки", None, None
        delete_alias(user_id, args[1])
        return f"Алиас '{args[1]}' удалён.", None, None

    if len(args) < 2:
        return "Укажите имя и команду. Пример: /ал 2атаки к+5 1к8+3", None, None

    name = args[0]
    command = " ".join(args[1:])
    save_alias(user_id, name, command)
    return f"Алиас '/{name}' сохранён.", None, None

# ---- Персонажи ----
@premium_only
def handle_character(mention, args, comment, user_id):
    if not args:
        chars = get_user_characters(user_id)
        active = get_active_character(user_id)
        if not chars:
            return "У вас нет персонажей. Создайте: /char Имя", None, None
        lines = ["*Ваши персонажи:*"]
        for name in chars:
            marker = "✅ " if name == active else ""
            lines.append(f"{marker}{name}")
        return "\n".join(lines), None, None

    if len(args) == 1:
        name = args[0]
        create_character(user_id, name)
        set_active_character(user_id, name)
        return f"Персонаж '{name}' создан и выбран как активный.", None, None

    if args[0] == "del":
        if len(args) < 2:
            return "Укажите имя персонажа для удаления.", None, None
        delete_character(user_id, args[1])
        return f"Персонаж '{args[1]}' удалён.", None, None

    active = get_active_character(user_id)
    if not active:
        return "Сначала выберите активного персонажа: /char Имя", None, None

    if args[0] == "set":
        if len(args) < 2:
            return "Укажите параметр и значение. Пример: /char set hp=20", None, None
        try:
            param, value = args[1].split("=", 1)
        except ValueError:
            return "Неверный формат. Используйте: /char set param=value", None, None
        set_character_stat(user_id, active, param, value)
        return f"Параметр '{param}' для персонажа '{active}' установлен: {value}", None, None

    if args[0] == "stats" or args[0] == "параметры":
        stats = get_all_character_stats(user_id, active)
        if not stats:
            return f"У персонажа '{active}' нет сохранённых параметров.", None, None
        lines = [f"*Параметры персонажа {active}:*"]
        for param, value in stats.items():
            lines.append(f"{param}: {value}")
        return "\n".join(lines), None, None

    if args[0] == "hp":
        if len(args) < 2:
            return "Укажите изменение. Пример: /char hp -5 или /char hp +10", None, None
        try:
            change = int(args[1])
        except ValueError:
            return "Укажите число. Пример: /char hp -5", None, None
        current_hp = get_character_stat(user_id, active, "hp")
        if current_hp is None:
            current_hp = "0"
        new_hp = int(current_hp) + change
        set_character_stat(user_id, active, "hp", str(new_hp))
        return f"Хиты персонажа '{active}': {current_hp} → {new_hp} ({change:+d})", None, None

    if args[0] == "+lvl":
        current_lvl = get_character_stat(user_id, active, "lvl")
        if current_lvl is None:
            current_lvl = "0"
        new_lvl = int(current_lvl) + 1
        set_character_stat(user_id, active, "lvl", str(new_lvl))
        return f"Уровень персонажа '{active}': {current_lvl} → {new_lvl}", None, None

    return "Неизвестная команда. Доступно: /char Имя, /char del Имя, /char set param=value, /char stats, /char hp ±N, /char +lvl", None, None

# ---- Монстры ----
@premium_only
def handle_monster(mention, args, comment, user_id):
    if not args:
        monsters = get_user_monsters(user_id)
        active = get_active_monster(user_id)
        if not monsters:
            return "У вас нет монстров. Создайте: /мон Имя", None, None
        lines = ["*Ваши монстры:*"]
        for name in monsters:
            marker = "✅ " if name == active else ""
            lines.append(f"{marker}{name}")
        return "\n".join(lines), None, None

    if len(args) == 1:
        name = args[0]
        create_monster(user_id, name)
        set_active_monster(user_id, name)
        return f"Монстр '{name}' создан и выбран как активный.", None, None

    if args[0] == "del":
        if len(args) < 2:
            return "Укажите имя монстра для удаления.", None, None
        delete_monster(user_id, args[1])
        return f"Монстр '{args[1]}' удалён.", None, None

    active = get_active_monster(user_id)
    if not active:
        return "Сначала выберите активного монстра: /мон Имя", None, None

    if args[0] == "set":
        if len(args) < 2:
            return "Укажите параметр и значение. Пример: /мон set hp=20", None, None
        try:
            param, value = args[1].split("=", 1)
        except ValueError:
            return "Неверный формат. Используйте: /мон set param=value", None, None
        set_monster_stat(user_id, active, param, value)
        return f"Параметр '{param}' для монстра '{active}' установлен: {value}", None, None

    if args[0] == "stats" or args[0] == "параметры":
        stats = get_all_monster_stats(user_id, active)
        if not stats:
            return f"У монстра '{active}' нет сохранённых параметров.", None, None
        lines = [f"*Параметры монстра {active}:*"]
        for param, value in stats.items():
            lines.append(f"{param}: {value}")
        return "\n".join(lines), None, None

    return "Неизвестная команда. Доступно: /мон Имя, /мон del Имя, /мон set param=value, /мон stats", None, None