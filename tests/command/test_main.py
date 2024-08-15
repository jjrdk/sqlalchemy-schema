from collections.abc import Sequence
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
from sqlalchemy_to_json_schema.types import Decision, Format, Layout, Walker


@pytest.fixture
def mock_driver(mocker: MockerFixture) -> Mock:
    return mocker.patch("sqlalchemy_to_json_schema.command.driver.Driver", autospec=True)


@pytest.fixture
def mock_load_module_or_symbol(mock_driver: Mock, mocker: MockerFixture) -> Mock:
    return mocker.patch(
        "sqlalchemy_to_json_schema.command.main.load_module_or_symbol",
        return_value=mock_driver,
        autospec=True,
    )


@pytest.mark.parametrize("targets", [["my_module"]])
def test_main_defaults(
    mock_driver: Mock, mock_load_module_or_symbol: Mock, targets: Sequence[str]
) -> None:
    """
    ARRANGE CLI args
    ACT calling the driver's method
    ASSERT matches the expected
        AND using all defaults
    """
    # ARRANGE
    runner = CliRunner()

    # ACT
    actual = runner.invoke(main, targets)

    # ASSERT
    assert actual.exit_code == 0

    mock_load_module_or_symbol.assert_called_once_with(DEFAULT_DRIVER)

    mock_driver.assert_called_once_with(DEFAULT_WALKER, DEFAULT_DECISION, DEFAULT_LAYOUT)
    mock_driver.return_value.run.assert_called_once_with(
        tuple(targets), filename=None, format=None
    )


@pytest.mark.parametrize("targets", [["my_module"]])
@pytest.mark.parametrize("walker", Walker)
@pytest.mark.parametrize("decision", Decision)
@pytest.mark.parametrize("layout", Layout)
@pytest.mark.parametrize("format", Format)
@pytest.mark.parametrize("out", [Path("output.txt").absolute()])
def test_main(
    mock_driver: Mock,
    mock_load_module_or_symbol: Mock,
    targets: Sequence[str],
    walker: Walker,
    decision: Decision,
    layout: Layout,
    format: Format,
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
    cli_args.extend(targets)

    # ACT
    actual = runner.invoke(main, cli_args)

    # ASSERT
    assert actual.exit_code == 0

    mock_load_module_or_symbol.assert_called_once_with(DEFAULT_DRIVER)

    mock_driver.assert_called_once_with(walker, decision, layout)
    mock_driver.return_value.run.assert_called_once_with(
        tuple(targets), filename=out, format=format
    )
