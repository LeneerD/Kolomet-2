import pytest
from handlers.basic import set_tables, roll_table, roll_spark, roll_exploration

# Фиктивные данные для тестов
MOCK_TABLES = {
    "tables": {
        "melee": {
            "2": ["Skill A", "Desc A"],
            "7": ["Skill B", "Desc B"],
            "12": ["Skill C", "Desc C"]
        }
    },
    "spark": {
        "1": "Spark 1",
        "5": "Spark 5",
        "10": "Spark 10"
    },
    "spark_max_key": 10,
    "exploration_tables": {
        "common": {
            "4": "Common 4",
            "8": "Common 8"
        },
        "rare": {
            "5": "Rare 5"
        },
        "legendary": {
            "6": "Legendary 6"
        }
    }
}

@pytest.fixture
def mock_tables():
    set_tables(MOCK_TABLES)
    yield
    set_tables({})  # очистка после теста

class TestTables:
    def test_roll_table_success(self, mock_tables):
        result, error, _ = roll_table("melee")
        assert error is None
        # result содержит строку типа "2d6 → ... — Skill A — Desc A"
        assert "Skill A" in result or "Skill B" in result or "Skill C" in result

    def test_roll_table_not_found(self, mock_tables):
        result, error, _ = roll_table("unknown")
        assert error == "Таблица 'unknown' не найдена. Доступны: melee"

    def test_roll_table_empty(self):
        # Если таблицы не загружены
        set_tables({})
        result, error, _ = roll_table("melee")
        assert error == "Таблицы навыков не загружены."

    def test_roll_spark_by_number(self, mock_tables):
        roll, result = roll_spark(5)
        assert roll == 5
        assert result == "Spark 5"

    def test_roll_spark_random(self, mock_tables):
        roll, result = roll_spark()
        assert roll is not None
        assert 1 <= roll <= 10
        assert result in ["Spark 1", "Spark 5", "Spark 10"]  # или другие в зависимости от рандома

    def test_roll_spark_not_found(self, mock_tables):
        roll, result = roll_spark(999)
        assert roll is None
        assert result == "Запись 999 не найдена"

    def test_roll_exploration_direct(self, mock_tables):
        result, error, _ = roll_exploration("common", direct_value=4)
        assert error is None
        assert "Common 4" in result

        result, error, _ = roll_exploration("rare", direct_value=5)
        assert "Rare 5" in result

    def test_roll_exploration_roll(self, mock_tables):
        # Проверяем, что бросок даёт результат
        result, error, _ = roll_exploration("common", num_dice=2)
        assert error is None
        assert "Бросок 2d6" in result

    def test_roll_exploration_unknown_category(self, mock_tables):
        result, error, _ = roll_exploration("unknown")
        assert "Неизвестная категория" in error