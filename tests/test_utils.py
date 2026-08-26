import pytest
from utils import generate_stats, flip_coin, random_number

class TestUtils:
    def test_generate_stats(self):
        stats = generate_stats()
        assert len(stats) == 6
        for val in stats:
            assert 3 <= val <= 18  # 3d6 (сумма трёх наибольших из 4d6) даёт от 3 до 18

    def test_flip_coin(self):
        # Просто проверяем, что возвращает строку
        result = flip_coin()
        assert result in ("Орёл!", "Решка!")

    def test_random_number_no_args(self):
        result, error = random_number([])
        assert error is None
        assert 0 <= result <= 100

    def test_random_number_two_args(self):
        result, error = random_number(["1", "100"])
        assert error is None
        assert 1 <= result <= 100

        result, error = random_number(["100", "1"])
        assert error is None  # сортировка
        assert 1 <= result <= 100

    def test_random_number_errors(self):
        result, error = random_number(["abc", "10"])
        assert error == "Введите два целых числа. Пример: /rand 1 100"

        result, error = random_number(["5"])
        assert error == "Укажите два числа через пробел. Пример: /rand 1 100"