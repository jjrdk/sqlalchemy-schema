from pathlib import Path
from unittest.mock import Mock

import pytest
from click.testing import CliRunner
from pytest_mock import MockerFixture

from sqlalchemy_to_json_schema.command.main import (
    DEFAULT_DECISION,
    DEFAULT_DRIVER,
    DEFAULT_LAYOUT,
    DEFAULT_WALKER,
    main,
)
from sqlalchemy_to_json_schema.types import (
    DecisionChoice,
    FormatChoice,
    LayoutChoice,
    WalkerChoice,
)


@pytest.fixture
def mock_driver(mocker: MockerFixture) -> Mock:
    return mocker.patch("sqlalchemy_to_json_schema.command.driver.Driver", autospec=True)


@pytest.fixture
def mock_import_symbol(mock_driver: Mock, mocker: MockerFixture) -> Mock:
    return mocker.patch(
        "sqlalchemy_to_json_schema.command.main.import_symbol",
        return_value=mock_driver,
        autospec=True,
    )


@pytest.mark.parametrize("target", ["my_module"])
def test_main_defaults(mock_driver: Mock, mock_import_symbol: Mock, target: str) -> None:
    """
    ARRANGE CLI args
    ACT calling the driver's method
    ASSERT matches the expected
        AND using all defaults
    """
    # ARRANGE
    runner = CliRunner()

    cli_args = [target]

    # ACT
    actual = runner.invoke(main, cli_args)

    # ASSERT
    assert actual.exit_code == 0

    mock_import_symbol.assert_called_once_with(DEFAULT_DRIVER, cwd=True)

    mock_driver.assert_called_once_with(DEFAULT_WALKER, DEFAULT_DECISION, DEFAULT_LAYOUT)
    mock_driver.return_value.run.assert_called_once_with(target, None, format=None)


@pytest.mark.parametrize("target", ["my_module"])
@pytest.mark.parametrize("walker", WalkerChoice)
@pytest.mark.parametrize("decision", DecisionChoice)
@pytest.mark.parametrize("layout", LayoutChoice)
@pytest.mark.parametrize("format", FormatChoice)
@pytest.mark.parametrize("out", [Path("output.txt").absolute()])
def test_main(
    mock_driver: Mock,
    mock_import_symbol: Mock,
    target: str,
    walker: WalkerChoice,
    decision: DecisionChoice,
    layout: LayoutChoice,
    format: FormatChoice,
    out: Path,
) -> None:
    """
    ARRANGE CLI args
        AND all combinations for CLI options
    ACT calling the driver's method
    ASSERT matches the expected
    """
    # ARRANGE
    runner = CliRunner()

    cli_args = [
        target,
        "--walker",
        walker.value,
        "--decision",
        decision.value,
        "--layout",
        layout.value,
        "--format",
        format.value,
        "--out",
        out.as_posix(),
    ]

    # ACT
    actual = runner.invoke(main, cli_args)

    # ASSERT
    assert actual.exit_code == 0

    mock_driver.assert_called_once_with(walker, decision, layout)
    mock_driver.return_value.run.assert_called_once_with(target, out, format=format)
