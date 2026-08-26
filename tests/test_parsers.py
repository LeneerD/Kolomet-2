import pytest
from parsers import parse_single_component, parse_expression

class TestParsers:
    def test_parse_single_component_simple(self):
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
        assert 1 <= result <= 6

    def test_parse_single_component_with_explode(self):
        result, error, details = parse_single_component("2d6!1")
        assert error is None
        assert result >= 2

        result, error, details = parse_single_component("1d6!!")
        assert error is None
        assert result is not None

    def test_parse_single_component_adv_dis(self):
        result, error, details = parse_single_component("adv")
        assert error is None
        assert 1 <= result <= 20

        result, error, details = parse_single_component("dis")
        assert error is None
        assert 1 <= result <= 20

        result, error, details = parse_single_component("adv+2")
        assert error is None
        assert 3 <= result <= 22

    def test_parse_single_component_errors(self):
        result, error, details = parse_single_component("")
        assert error == "Пустой компонент"

        result, error, details = parse_single_component("abc")
        assert "Не удалось распознать" in error

        result, error, details = parse_single_component("2+3")
        assert error == "Не удалось распознать '2+3'. Пример: 2d6+3"

        result, error, details = parse_single_component("abc d6")
        assert "Количество кубиков должно быть числом" in error

        result, error, details = parse_single_component("200d6")
        assert "слишком много кубиков" in error.lower()

    def test_parse_expression(self):
        result, error, details = parse_expression("2d6 + 3")
        assert error is None
        assert isinstance(result, int)
        assert 5 <= result <= 15

        result, error, details = parse_expression("d20 - 5")
        assert error is None

        result, error, details = parse_expression("2d6 + 1d4 - 2")
        assert error is None
        assert 1 <= result <= 14

        result, error, details = parse_expression("")
        assert error == "Пустое выражение"