import pytest
from unittest.mock import MagicMock
from utils import is_donor
import config

@pytest.fixture
def mock_vk(mocker):
    """Мокает vk в модуле utils, чтобы избежать реальных вызовов."""
    mock = MagicMock()
    mock.method = MagicMock(return_value=False)  # по умолчанию возвращает False
    mocker.patch('utils.vk', mock)
    return mock

@pytest.mark.usefixtures("mock_vk")
class TestDonor:
    def test_is_donor_owner(self, mocker):
        mocker.patch.object(config, 'OWNER_ID', 123)
        assert is_donor(123) is True

    def test_is_donor_tester(self, mocker):
        mocker.patch('utils._testers', [456, 789])
        assert is_donor(456) is True
        assert is_donor(789) is True
        assert is_donor(111) is False  # не в списке, и vk вернёт False

    def test_is_donor_vk_donut(self, mock_vk):
        mock_vk.method.return_value = True
        assert is_donor(999) is True
        mock_vk.method.assert_called_once_with('donut.isDon', {'user_id': 999})

        mock_vk.method.reset_mock()
        mock_vk.method.return_value = False
        assert is_donor(888) is False
        mock_vk.method.assert_called_with('donut.isDon', {'user_id': 888})

    def test_is_donor_cache(self, mock_vk):
        mock_vk.method.return_value = True
        is_donor(555)  # первый вызов
        is_donor(555)  # второй вызов — должен использовать кеш
        assert mock_vk.method.call_count == 1