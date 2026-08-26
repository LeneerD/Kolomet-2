import pytest
from parsers import parse_single_component, parse_expression

class TestParsers:
    def test_parse_single_component_simple(self):
        # Обычные броски
        result, error, details = parse_single_component("2d6")
        assert error is None
        assert isinstance(result, int)
        assert 2 <= result <= 12
        assert details is not None

        result, error, details = parse_single_component("d20")
        assert error is None
        assert 1 <= result <= 20

        result, error, details = parse_single_component("d%")
        assert error is None
        assert 1 <= result <= 100

    def test_parse_single_component_with_mods(self):
        # С модификаторами
        result, error, details = parse_single_component("2d6+3")
        assert error is None
        assert 5 <= result <= 15

        result, error, details = parse_single_component("d10-2")
        assert error is None
        assert -1 <= result <= 8

    def test_parse_single_component_with_multiplier(self):
        result, error, details = parse_single_component("2d6x2")
        assert error is None
        assert 4 <= result <= 24

        result, error, details = parse_single_component("d4*3")
        assert error is None
        assert 3 <= result <= 12

    def test_parse_single_component_with_resist(self):
        result, error, details = parse_single_component("2d6r")
        assert error is None
        # Резист делит на 2, результат должен быть в пределах [1, 6]
        assert 1 <= result <= 6

    def test_parse_single_component_with_explode(self):
        result, error, details = parse_single_component("2d6!1")
        assert error is None
        # Проверяем, что результат не меньше суммы (но может быть больше)
        assert result >= 2

        result, error, details = parse_single_component("1d6!!")
        assert error is None
        # Может быть меньше (если выпала 1 и откатило)
        # Проверяем только что не None
        assert result is not None

    def test_parse_single_component_adv_dis(self):
        result, error, details = parse_single_component("adv")
        assert error is None
        assert 1 <= result <= 20

        result, error, details = parse_single_component("dis")
        assert error is None
        assert 1 <= result <= 20

        # С модификатором
        result, error, details = parse_single_component("adv+2")
        assert error is None
        assert 3 <= result <= 22

    def test_parse_single_component_errors(self):
        # Пустой компонент
        result, error, details = parse_single_component("")
        assert error == "Пустой компонент"

        # Неверный формат
        result, error, details = parse_single_component("abc")
        assert "Не удалось распознать" in error

        # Отсутствует d
        result, error, details = parse_single_component("2+3")
        assert "Отсутствует 'd'" in error

        # Некорректное количество
        result, error, details = parse_single_component("abc d6")
        assert "Количество кубиков должно быть числом" in error

        # Слишком много кубиков
        result, error, details = parse_single_component("200d6")
        assert "слишком много кубиков" in error.lower()

    def test_parse_expression(self):
        # Сложение
        result, error, details = parse_expression("2d6 + 3")
        assert error is None
        assert isinstance(result, int)
        assert 5 <= result <= 15

        # Вычитание
        result, error, details = parse_expression("d20 - 5")
        assert error is None

        # Смешанное
        result, error, details = parse_expression("2d6 + 1d4 - 2")
        assert error is None
        # Сумма от 2+1-2 =1 до 12+4-2=14
        assert 1 <= result <= 14

        # Пустое выражение
        result, error, details = parse_expression("")
        assert error == "Пустое выражение"