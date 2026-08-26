import os

VK_TOKEN = os.environ.get("VK_TOKEN")
GROUP_ID = os.environ.get("GROUP_ID")
OWNER_ID = os.environ.get("OWNER_ID")

if not VK_TOKEN or not GROUP_ID:
    raise Exception("VK_TOKEN и GROUP_ID должны быть заданы в переменных окружения!")

try:
    GROUP_ID = int(GROUP_ID)
    OWNER_ID = int(OWNER_ID) if OWNER_ID else None
except ValueError:
    raise Exception("GROUP_ID и OWNER_ID должны быть целыми числами!")

CONSTANTS = {
    "max_dice": 100,
    "max_dice_type": 1000,
    "default_exploration_dice": 3,
}

# ---- Пути к данным ----
DATA_DIR = "data"

TABLE_FILES = {
    "tables": os.path.join(DATA_DIR, "tables.json"),
    "injury": os.path.join(DATA_DIR, "injury.json"),
    "spark": os.path.join(DATA_DIR, "spark.json"),
    "exploration": os.path.join(DATA_DIR, "exploration.json"),
}

TESTERS_FILE = os.path.join(DATA_DIR, "testers.json")
NICKNAMES_FILE = os.path.join(DATA_DIR, "nicknames.json")
DB_PATH = os.path.join(DATA_DIR, "bot_data.db")