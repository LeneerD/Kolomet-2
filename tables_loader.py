import json
import os
import logging
from config import TABLE_FILES, DATA_DIR

logger = logging.getLogger(__name__)

# ---- Дефолтные данные (те же, что были) ----
DEFAULT_TABLES = {
    "melee": {
        "2": ["Patron Skill", "Pick one of the Skills offered by your patron."],
        "3": ["Stand Firm", "The first time a model with this Skill suffers a Down result on the Injury table, it is treated as a Minor Hit result instead."],
        "4": ["Parry", "Add -1 Dice to Success Rolls for Melee Attacks that target a model with this Skill."],
        "5": ["Close Quarter Combat", "Add +1 Dice and +1 Injury Dice to rolls for Melee Attacks made by a model with this Skill if it is in contact with a terrain piece."],
        "6": ["Relentless Charge", "Add +1 Dice to rolls for Melee Attacks made by a model with this Skill if it successfully charged earlier in the same Activation."],
        "7": ["Melee Proficiency", "Add +1 Dice to the Melee Characteristic of a model with this Skill."],
        "8": ["Strength of Samson", "Add +1 Injury Dice to rolls for Melee Attacks using a Melee Weapon made by a model with this Skill. In addition, a model with this Skill has the Strong keyword."],
        "9": ["Hard as Nails", "The first time a model with this Skill suffers a Down result on the Injury table, it is treated as a No Effect result instead."],
        "10": ["Surgical Strike", "Once per Activation, before you make an Injury Roll for a Melee Attack made by a model with this Skill, you can say that the roll has the Ignore Armour Keyword."],
        "11": ["Champion", "Melee Weapons that do not have the Cleave Keyword which are used by a model with this Skill gain the Cleave 2 Keyword. In addition, add -1 Dice to the Success Roll for the second Melee Attack made with each Melee Weapon that gains the Cleave Keyword."],
        "12": ["Patron Skill", "Pick one of the Skills offered by your patron."]
    },
    "ranged": {
        "2": ["Patron Skill", "Pick one of the Skills offered by your patron."],
        "3": ["Hunter", "Ranged Attacks made by a model with this Skill have the Ignore COVER Keyword."],
        "4": ["Gunslinger", "The following rules apply to a model with this Skill if it is armed with Ranged Weapons with the Pistol Keyword.\n\nIf it is equipped with 2 Weapons with the Pistol Keyword, it can take a Shoot ACTION with one and then immediately take a Shoot ACTION with the other.\nAdd the Assault and Ignore OFF-HAND WEAPON Keywords to any weapons that have the Pistol Keyword (unless they have them already)."],
        "5": ["Far Shot", "Add 6\" to the Range of the following Weapons when they are used by a model that has this Skill:\n\n- Any Weapon with the Pistol Keyword.\n- Any Weapon which has the word “Rifle” as part of its name (i.e. a Bolt Action Rifle, Assault Rifle etc).\n- Any Weapon which has either the word “Jezzail” or “Arquebus” as part of its name."],
        "6": ["Sharp Eyes", "Ranged Attacks made by a model with this Skill have the Ignore LONG RANGE Keyword."],
        "7": ["Ranged Proficiency", "Add +1 Dice to the Ranged Characteristic of a model with this Skill."],
        "8": ["Sniper's Nest", "Add +2 Dice to rolls for Ranged Attacks made with the Elevated Position modifier by a model with this Skill instead of +1 Dice."],
        "9": ["Point Blank", "When a model with this Skill makes a Melee Attack, it can use a Ranged Weapon and its Ranged Attack Characteristic instead of a Melee Weapon and its Melee Attack Characteristic. It must still be within 1\" of the target model to make the attack. It can also use the Ranged Weapon to make a Ranged Attack during the same Activation if it has the Assault Keyword."],
        "10": ["Hip Shot", "Ranged Weapons used by a model with this Skill count as having the Assault Keyword unless they already have it."],
        "11": ["Head Shot", "Ranged Attacks made by a model with this Skill have the Ignore Armour Keyword if the attack was a Critical Success."],
        "12": ["Patron Skill", "Pick one of the Skills offered by your patron."]
    },
    "stealth": {
        "2": ["Patron Skill", "Pick one of the Skills offered by your patron."],
        "3": ["Sixth Sense", "If a model with this Skill suffers a Down result on the Injury table, it is treated as a Minor Hit result instead if the model does not have any Blood Markers. If the model also has the Tough Keyword, once per game it can use the Keyword to change an Out of Action result to a Down result, and then use this Skill to change the Down result to No Effect."],
        "4": ["Assassinate", "Add +1 Dice to rolls for attacks made by a model with this Skill if the target has not yet been Activated this Turn."],
        "5": ["Shadow Walker", "Add -2 Dice to rolls for Ranged Attacks that target a model with this Skill at Long Range instead of -1 Dice."],
        "6": ["Athletic", "Add +1 Dice to Risky Success rolls for a model with this Skill when it Climbs, Jumps or makes a Diving Charge, and add -1 Injury Dice to Injury Rolls if it Falls."],
        "7": ["Sprinter", "Add +1 Dice to the Risky Success Roll for a model with this Skill that is taking a Dash ACTION."],
        "8": ["Disengage", "Enemy models cannot make a Melee Attack on a model with this Skill when it Retreats."],
        "9": ["Incoming", "When you roll the Charge Bonus for a model with this Skill, roll 1 extra D6 and use the single highest dice to determine the bonus."],
        "10": ["Nimble", "Do not halve the Movement Characteristic of a model with this Skill when it stands up."],
        "11": ["Dodge", "Add -1 Dice to rolls for Ranged Attacks that target a model with this Skill."],
        "12": ["Patron Skill", "Pick one of the Skills offered by your patron."]
    },
    "wildcard": {
        "2": ["Patron Skill", "Pick one of the Skills offered by your patron."],
        "3": ["War Luck", "A model with this Skill can suffer 1 extra Battle Scar before they are Unfit for Duty."],
        "4": ["'Tis but a Scratch", "You can re-roll the result on the Trauma Chart for a model with this Skill."],
        "5": ["Bad Company", "A model with this Skill does not count towards the number of Elite models that are in your Warband at the start of the Promotion step."],
        "6": ["Scavenger", "A model with this Skill has the Extra Dice Exploration Skill."],
        "7": ["Skill & Expertise", "When you give a model this Skill, choose 1 Action on that model's Warband Entry, or 1 Common Action apart from Fight or Shoot ActionS, and write it on your Warband Roster. Add +1 Dice to rolls made as part of the chosen Action when they are taken by this model."],
        "8": ["Show Off", "Add 1 dice to the Promotion Pool in the Promotion step for each model in your Warband with this Skill."],
        "9": ["Friends In High Places", "A model with this Skill has the Re-roll Dice Exploration Skill."],
        "10": ["Glory Hound", "At the end of each game, your Warband receives 1 extra  for each model with this Skill that is on the battlefield."],
        "11": ["War Stories", "When you are recording the Experience Points earned by the models in your Warband in the Campaign Phase, you can give each model with the Elite Keyword that does not also have this Skill +1 extra Experience Point. You can’t pick the model with the Skill itself. A Warband can only have one model with this Skill."],
        "12": ["Patron Skill", "Pick one of the Skills offered by your patron."]
    }
}

DEFAULT_INJURY = {
    "11": ["Dead", "The wound proved to be fatal. Remove the model and its Battlekit from your Warband Roster."],
    "12": ["Captured", "The enemy captures the model. Before continuing the Trauma Step, you and your opponent from the game can negotiate a ransom price in  for the release of the model. If the ransom is not paid, the captured model is executed – remove them from your Warband Roster. If the ransom is paid, transfer the  from your Strongbox to your opponent’s, and treat this result as a Full Recovery. Continue with the Trauma Step after resolving the outcome of the ransom."],
    "13": ["Severe Nerve Damage", "All Success Rolls you take for this model are treated as being Risky Success Rolls, unless they are Risky Success Rolls already, in which case there is no additional penalty."],
    "14": ["Hand Wound", "Randomly determine which hand has been injured. Add -1 Dice to rolls for attacks made for this model with a Melee Weapon that is held (or jointly held) by the injured hand."],
    "15": ["Lost An Eye", "Add -1 Dice to rolls for Ranged Attacks made for this model. If this model receives this injury for a second time, they are blinded and you must remove them from your Warband Roster instead of re-rolling the result. Treat this injury as a Full Recovery if it is inflicted on a Sniper Priest."],
    "16": ["Chest Wound", "Add +1 Injury Dice to Injury Rolls for attacks that target this model."],
    "21": ["Insomniac", "This model must always be the first model you deploy in any game it takes part in, and loses the Infiltrator Keyword if it has it."],
    "22": ["Head Wound", "This model can no longer gain Experience Points. You can assign Promotion Dice to this model as if it were a Troop in the Promotions and Experience Step. If one of its assigned Promotion Dice rolls a “6”, it regains the ability to gain Experience Points, although the Battle Scar remains."],
    "23": ["Shell Shocked", "Roll a D6 the first time this model is deployed during a game. On a 1-2, add -1 Dice to rolls for this model for the rest of the game."],
    "24": ["Dark Memory", "Write down the name of the Warband from the game where this injury was received. Add -1 Dice to rolls for Melee Attacks made by this model if the target is a model from the Warband you have written down."],
    "25": ["Paranoid", "This model cannot be deployed within 8\" of a friendly model. Friendly models can be deployed within 8\" of this model after it has been deployed."],
    "26": ["Lost Arm", "This model cannot use Battlekit that requires 2 hands, and can only use one piece of Battlekit that requires 1 hand."],
    "31": ["Leg Wound", "Subtract 2\" from this model’s Movement Characteristic. In addition, add -1 Dice to the Risky Success Roll for this model when it takes a Dash Action."],
    "32": ["Expensive Treatment", "The model’s wounds require constant treatment. Before you can deploy this model, you must deduct 10  from your Warband’s Strongbox. This payment does not count towards your Warband’s Threshold Value."],
    "33": ["Possessed", "When this model is Activated, if it is more than 1” from any enemy models the first Action that it takes must take a Dash Action, even if another rule states that it cannot take a Dash Action. In addition, the first 3” of this move must be in a straight line directly away from its starting position, if it is possible for it to do so. If the model is Down at the start of the Activation, it will stand up if it can do so and must then attempt to move 3” in a straight line away from its starting position."],
    "34": ["Muscle Damage", "This model cannot have Battlekit that has the Heavy Keyword. Any that it has when the Injury is suffered is lost."],
    "35": ["Minor Wound", "This model cannot be used in the next game."],
    "36": ["Robbed", "All of the model’s Battlekit is lost, unless it is Battlekit that cannot be lost or removed during a campaign. It does not receive an Injury or a Battle Scar"],
    "41": ["Full Recovery", "The model has survived the battle with no ill effects. It does not receive an Injury or a Battle Scar."],
    "42": ["Full Recovery", "The model has survived the battle with no ill effects. It does not receive an Injury or a Battle Scar."],
    "43": ["Full Recovery", "The model has survived the battle with no ill effects. It does not receive an Injury or a Battle Scar."],
    "44": ["Full Recovery", "The model has survived the battle with no ill effects. It does not receive an Injury or a Battle Scar."],
    "45": ["Full Recovery", "The model has survived the battle with no ill effects. It does not receive an Injury or a Battle Scar."],
    "46": ["Full Recovery", "The model has survived the battle with no ill effects. It does not receive an Injury or a Battle Scar."],
    "47": ["Full Recovery", "The model has survived the battle with no ill effects. It does not receive an Injury or a Battle Scar."],
    "48": ["Full Recovery", "The model has survived the battle with no ill effects. It does not receive an Injury or a Battle Scar."],
    "49": ["Full Recovery", "The model has survived the battle with no ill effects. It does not receive an Injury or a Battle Scar."],
    "50": ["Full Recovery", "The model has survived the battle with no ill effects. It does not receive an Injury or a Battle Scar."],
    "51": ["Full Recovery", "The model has survived the battle with no ill effects. It does not receive an Injury or a Battle Scar."],
    "52": ["Full Recovery", "The model has survived the battle with no ill effects. It does not receive an Injury or a Battle Scar."],
    "53": ["Full Recovery", "The model has survived the battle with no ill effects. It does not receive an Injury or a Battle Scar."],
    "54": ["Full Recovery", "The model has survived the battle with no ill effects. It does not receive an Injury or a Battle Scar."],
    "55": ["Full Recovery", "The model has survived the battle with no ill effects. It does not receive an Injury or a Battle Scar."],
    "56": ["Full Recovery", "The model has survived the battle with no ill effects. It does not receive an Injury or a Battle Scar."],
    "57": ["Full Recovery", "The model has survived the battle with no ill effects. It does not receive an Injury or a Battle Scar."],
    "58": ["Full Recovery", "The model has survived the battle with no ill effects. It does not receive an Injury or a Battle Scar."],
    "59": ["Full Recovery", "The model has survived the battle with no ill effects. It does not receive an Injury or a Battle Scar."],
    "60": ["Full Recovery", "The model has survived the battle with no ill effects. It does not receive an Injury or a Battle Scar."],
    "61": ["Full Recovery", "The model has survived the battle with no ill effects. It does not receive an Injury or a Battle Scar."],
    "62": ["Full Recovery", "The model has survived the battle with no ill effects. It does not receive an Injury or a Battle Scar."],
    "63": ["Full Recovery", "The model has survived the battle with no ill effects. It does not receive an Injury or a Battle Scar."],
    "64": ["Hardened", "This model gains the Negate Fear Keyword. It does not receive an Injury or a Battle Scar."],
    "65": ["Bitter Lessons", "This model gains D3 extra Experience Points. It does not receive an Injury or a Battle Scar."],
    "66": ["Prominent Scar", "Write down the name of the Warband from the game where this injury was received. Add +1 Dice to rolls for Melee Attacks made by this model if the target is a model from the Warband you have written down. It does not receive an Injury or a Battle Scar."]
}

DEFAULT_SPARK = {
    "1": "В 6\" от модели Варлорда все союзные юниты получают Benefit of Cover (но не себе)",
    "2": "Если юнит противника совершает Фоллбек от юнита Варлорда, то мув юнита противника уменьшается на 2",
    "3": "+1 OC",
}

DEFAULT_EXPLORATION = {
    "common": {},
    "rare": {},
    "legendary": {}
}

# ---- Функции для работы с папкой данных ----
def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        logger.info(f"Создана папка {DATA_DIR}")

def ensure_file(filename, default_data):
    ensure_data_dir()
    if not os.path.exists(filename):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Создан файл {filename}")
        except IOError as e:
            logger.error(f"Не удалось создать файл {filename}: {e}")
        return True
    return False

def validate_tables(data):
    if not isinstance(data, dict):
        return False, "tables.json должен быть словарём"
    for table_name, table in data.items():
        if not isinstance(table, dict):
            return False, f"Таблица '{table_name}' должна быть словарём"
        for key, value in table.items():
            if not isinstance(key, str) or not key.isdigit():
                return False, f"Неверный ключ '{key}' в таблице '{table_name}'"
            if not (isinstance(value, list) and len(value) >= 2):
                return False, f"Значение для ключа '{key}' должно быть списком из двух элементов"
    return True, None

def validate_injury(data):
    if not isinstance(data, dict):
        return False, "injury.json должен быть словарём"
    for key, value in data.items():
        if not isinstance(key, str) or not key.isdigit():
            return False, f"Неверный ключ '{key}'"
        if not (isinstance(value, list) and len(value) >= 2):
            return False, f"Значение для ключа '{key}' должно быть списком из двух элементов"
    return True, None

def validate_spark(data):
    if not isinstance(data, dict):
        return False, "spark.json должен быть словарём"
    for key, value in data.items():
        if not isinstance(key, str) or not key.isdigit():
            return False, f"Неверный ключ '{key}'"
        if not isinstance(value, str):
            return False, f"Значение для ключа '{key}' должно быть строкой"
    return True, None

def validate_exploration(data):
    if not isinstance(data, dict):
        return False, "exploration.json должен быть словарём"
    for cat in ('common', 'rare', 'legendary'):
        if cat not in data:
            return False, f"Отсутствует категория '{cat}'"
        if not isinstance(data[cat], dict):
            return False, f"Категория '{cat}' должна быть словарём"
        for key, value in data[cat].items():
            if not isinstance(key, str) or not key.isdigit():
                return False, f"Неверный ключ '{key}' в категории '{cat}'"
            if not isinstance(value, str):
                return False, f"Значение для ключа '{key}' должно быть строкой"
    return True, None

def load_json_file(filename, default_data, validator=None):
    ensure_file(filename, default_data)
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if validator:
            valid, error = validator(data)
            if not valid:
                logger.warning(f"Ошибка валидации {filename}: {error}. Перезапись дефолтными.")
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(default_data, f, ensure_ascii=False, indent=2)
                return default_data
        return data
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Ошибка чтения {filename}: {e}. Перезапись дефолтными.")
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, ensure_ascii=False, indent=2)
        except IOError as e2:
            logger.error(f"Не удалось перезаписать {filename}: {e2}")
        return default_data

def load_all_tables():
    tables = load_json_file(TABLE_FILES["tables"], DEFAULT_TABLES, validate_tables)
    injury = load_json_file(TABLE_FILES["injury"], DEFAULT_INJURY, validate_injury)
    spark = load_json_file(TABLE_FILES["spark"], DEFAULT_SPARK, validate_spark)
    exploration_data = load_json_file(TABLE_FILES["exploration"], DEFAULT_EXPLORATION, validate_exploration)

    spark_max_key = max(map(int, spark.keys())) if spark else 0

    return {
        "tables": tables,
        "injury": injury,
        "spark": spark,
        "spark_max_key": spark_max_key,
        "exploration_data": exploration_data,
        "exploration_tables": {
            "common": exploration_data.get("common", {}),
            "rare": exploration_data.get("rare", {}),
            "legendary": exploration_data.get("legendary", {})
        }
    }