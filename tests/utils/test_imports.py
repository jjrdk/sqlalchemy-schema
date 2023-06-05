import pytest

from sqlalchemy_to_json_schema.utils.imports import load_module_or_symbol
from tests.fixtures.models import user


@pytest.mark.parametrize(
    "module_path, expected_result",
    [
        pytest.param("tests.fixtures.models.user:User", user.User, id="symbol specified"),
        pytest.param("tests.fixtures.models.user", user, id="symbol not specified"),
    ],
)
def test_load_module_or_symbol(module_path: str, expected_result: object):
    """
    ARRANGE Prepare the module path and expected result.
    ACT Call the load_module_or_symbol function with the module path.
    ASSERT Check if the returned result matches the expected result.
    """
    actual = load_module_or_symbol(module_path)

    assert actual == expected_result


def test_load_module_or_symbol_with_invalid_module():
    """
    ARRANGE Prepare an invalid module path.
    ACT Call the load_module_or_symbol function with the invalid module path.
    ASSERT Check if it raises an ImportError.
    """
    with pytest.raises(ImportError):
        load_module_or_symbol("invalid_module_name:func_name")


def test_load_module_or_symbol_with_no_module_and_symbol():
    """
    ARRANGE Prepare an empty module path.
    ACT Call the load_module_or_symbol function with the empty module path.
    ASSERT Check if it raises a ValueError.
    """
    with pytest.raises(ValueError):
        load_module_or_symbol(":symbol_name")
