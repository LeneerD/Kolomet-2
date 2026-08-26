import pytest
from unittest.mock import MagicMock
from utils import is_donor, reload_testers, load_testers

@pytest.fixture
def mock_vk_method(mocker):
    """Мокает vk.method, возвращая заданное значение."""
    mock = mocker.patch('utils.vk.method')
    return mock

@pytest.fixture
def mock_owner(mocker):
    """Устанавливает OWNER_ID в конфиге."""
    mocker.patch('config.OWNER_ID', 123)

@pytest.fixture
def temp_testers_file(tmp_path, mocker):
    """Создаёт временный файл testers.json и подменяет TESTERS_FILE в конфиге."""
    testers_file = tmp_path / "testers.json"
    testers_file.write_text('{"testers": [456, 789]}', encoding='utf-8')
    mocker.patch('config.TESTERS_FILE', str(testers_file))
    # Перезагружаем тестеры, чтобы они подхватились
    reload_testers()
    yield testers_file
    # После теста можно ничего не делать

class TestDonor:
    def test_is_donor_owner(self, mock_owner):
        # Владелец всегда True
        assert is_donor(123) is True

    def test_is_donor_tester(self, temp_testers_file):
        # Тестировщики из временного файла
        assert is_donor(456) is True
        assert is_donor(789) is True
        assert is_donor(111) is False

    def test_is_donor_vk_donut(self, mock_vk_method):
        # Мокаем vk.method, чтобы возвращал True/False
        mock_vk_method.return_value = True
        assert is_donor(999) is True
        mock_vk_method.assert_called_once_with('donut.isDon', {'user_id': 999})

        mock_vk_method.reset_mock()
        mock_vk_method.return_value = False
        assert is_donor(888) is False
        mock_vk_method.assert_called_with('donut.isDon', {'user_id': 888})

    def test_is_donor_cache(self, mock_vk_method):
        # Проверяем кеширование
        mock_vk_method.return_value = True
        is_donor(555)
        is_donor(555)  # второй раз не должен вызывать метод
        assert mock_vk_method.call_count == 1