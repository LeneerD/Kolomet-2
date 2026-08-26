import pytest
import sqlite3
from db import get_connection, init_db, save_alias, get_alias, delete_alias, create_character, get_user_characters

@pytest.fixture
def db_connection(monkeypatch):
    """Подменяет DB_PATH на временную БД в памяти."""
    monkeypatch.setattr('config.DB_PATH', ':memory:')
    init_db()
    yield
    # База в памяти удаляется автоматически после закрытия соединений

class TestDB:
    def test_save_and_get_alias(self, db_connection):
        save_alias(123, "myroll", "2d6+3")
        result = get_alias(123, "myroll")
        assert result == "2d6+3"

        # Несуществующий алиас
        result = get_alias(123, "unknown")
        assert result is None

    def test_delete_alias(self, db_connection):
        save_alias(123, "roll", "d20")
        delete_alias(123, "roll")
        result = get_alias(123, "roll")
        assert result is None

    def test_get_user_aliases(self, db_connection):
        save_alias(123, "a1", "cmd1")
        save_alias(123, "a2", "cmd2")
        save_alias(456, "a3", "cmd3")
        aliases = get_user_aliases(123)
        assert len(aliases) == 2
        assert ("a1", "cmd1") in aliases
        assert ("a2", "cmd2") in aliases

    def test_create_and_get_characters(self, db_connection):
        create_character(123, "Hero")
        create_character(123, "Mage")
        create_character(456, "Villain")
        chars = get_user_characters(123)
        assert "Hero" in chars
        assert "Mage" in chars
        assert "Villain" not in chars