import pytest
import db
from db import save_alias, get_alias, delete_alias, create_character, get_user_characters, get_user_aliases

@pytest.fixture
def db_connection(monkeypatch, tmp_path):
    db_file = tmp_path / "test.db"
    monkeypatch.setattr(db, 'DB_PATH', str(db_file))
    db.init_db()  # теперь создаст таблицы в новом пути
    yield
    # после теста файл удалится автоматически

class TestDB:
    def test_save_and_get_alias(self, db_connection):
        save_alias(123, "myroll", "2d6+3")
        result = get_alias(123, "myroll")
        assert result == "2d6+3"

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