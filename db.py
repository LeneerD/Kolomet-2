import sqlite3
from config import DB_PATH

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS aliases (
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                command TEXT NOT NULL,
                PRIMARY KEY (user_id, name)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS characters (
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                PRIMARY KEY (user_id, name)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS character_stats (
                user_id INTEGER NOT NULL,
                char_name TEXT NOT NULL,
                param TEXT NOT NULL,
                value TEXT NOT NULL,
                PRIMARY KEY (user_id, char_name, param)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS active_character (
                user_id INTEGER PRIMARY KEY,
                char_name TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monsters (
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                PRIMARY KEY (user_id, name)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monster_stats (
                user_id INTEGER NOT NULL,
                monster_name TEXT NOT NULL,
                param TEXT NOT NULL,
                value TEXT NOT NULL,
                PRIMARY KEY (user_id, monster_name, param)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS active_monster (
                user_id INTEGER PRIMARY KEY,
                monster_name TEXT NOT NULL
            )
        ''')
        conn.commit()

# ---- Алиасы ----
def save_alias(user_id, name, command):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO aliases (user_id, name, command) VALUES (?, ?, ?)",
            (user_id, name, command)
        )
        conn.commit()

def get_alias(user_id, name):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT command FROM aliases WHERE user_id = ? AND name = ?",
            (user_id, name)
        )
        result = cursor.fetchone()
        return result[0] if result else None

def get_user_aliases(user_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name, command FROM aliases WHERE user_id = ?",
            (user_id,)
        )
        return cursor.fetchall()

def delete_alias(user_id, name):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM aliases WHERE user_id = ? AND name = ?",
            (user_id, name)
        )
        conn.commit()

# ---- Персонажи ----
def create_character(user_id, name):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO characters (user_id, name) VALUES (?, ?)",
            (user_id, name)
        )
        conn.commit()

def delete_character(user_id, name):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM characters WHERE user_id = ? AND name = ?",
            (user_id, name)
        )
        cursor.execute(
            "DELETE FROM character_stats WHERE user_id = ? AND char_name = ?",
            (user_id, name)
        )
        cursor.execute(
            "DELETE FROM active_character WHERE user_id = ? AND char_name = ?",
            (user_id, name)
        )
        conn.commit()

def get_user_characters(user_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM characters WHERE user_id = ?",
            (user_id,)
        )
        return [row[0] for row in cursor.fetchall()]

def set_character_stat(user_id, char_name, param, value):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO character_stats (user_id, char_name, param, value) VALUES (?, ?, ?, ?)",
            (user_id, char_name, param, value)
        )
        conn.commit()

def get_character_stat(user_id, char_name, param):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT value FROM character_stats WHERE user_id = ? AND char_name = ? AND param = ?",
            (user_id, char_name, param)
        )
        result = cursor.fetchone()
        return result[0] if result else None

def get_all_character_stats(user_id, char_name):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT param, value FROM character_stats WHERE user_id = ? AND char_name = ?",
            (user_id, char_name)
        )
        result = cursor.fetchall()
        return dict(result) if result else {}

def set_active_character(user_id, char_name):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO active_character (user_id, char_name) VALUES (?, ?)",
            (user_id, char_name)
        )
        conn.commit()

def get_active_character(user_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT char_name FROM active_character WHERE user_id = ?",
            (user_id,)
        )
        result = cursor.fetchone()
        return result[0] if result else None

# ---- Монстры ----
def create_monster(user_id, name):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO monsters (user_id, name) VALUES (?, ?)",
            (user_id, name)
        )
        conn.commit()

def delete_monster(user_id, name):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM monsters WHERE user_id = ? AND name = ?",
            (user_id, name)
        )
        cursor.execute(
            "DELETE FROM monster_stats WHERE user_id = ? AND monster_name = ?",
            (user_id, name)
        )
        cursor.execute(
            "DELETE FROM active_monster WHERE user_id = ? AND monster_name = ?",
            (user_id, name)
        )
        conn.commit()

def get_user_monsters(user_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM monsters WHERE user_id = ?",
            (user_id,)
        )
        return [row[0] for row in cursor.fetchall()]

def set_monster_stat(user_id, monster_name, param, value):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO monster_stats (user_id, monster_name, param, value) VALUES (?, ?, ?, ?)",
            (user_id, monster_name, param, value)
        )
        conn.commit()

def get_monster_stat(user_id, monster_name, param):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT value FROM monster_stats WHERE user_id = ? AND monster_name = ? AND param = ?",
            (user_id, monster_name, param)
        )
        result = cursor.fetchone()
        return result[0] if result else None

def get_all_monster_stats(user_id, monster_name):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT param, value FROM monster_stats WHERE user_id = ? AND monster_name = ?",
            (user_id, monster_name)
        )
        result = cursor.fetchall()
        return dict(result) if result else {}

def set_active_monster(user_id, monster_name):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO active_monster (user_id, monster_name) VALUES (?, ?)",
            (user_id, monster_name)
        )
        conn.commit()

def get_active_monster(user_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT monster_name FROM active_monster WHERE user_id = ?",
            (user_id,)
        )
        result = cursor.fetchone()
        return result[0] if result else None