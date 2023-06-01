import json
from functools import partial
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Callable, Optional

import pytest
import yaml
from yaml import Loader

from sqlalchemy_to_json_schema.command.driver import Driver
from sqlalchemy_to_json_schema.types import (
    DecisionChoice,
    FormatChoice,
    LayoutChoice,
    WalkerChoice,
)


@pytest.fixture
def temp_filename() -> Path:
    with NamedTemporaryFile() as f:
        yield Path(f.name)


@pytest.mark.parametrize("walker", WalkerChoice)
@pytest.mark.parametrize("decision", DecisionChoice)
@pytest.mark.parametrize("layout", LayoutChoice)
@pytest.mark.parametrize(
    "format, file_loader",
    [
        pytest.param(None, json.loads),
        pytest.param(FormatChoice.JSON, json.loads),
        pytest.param(FormatChoice.YAML, partial(yaml.load, Loader=Loader)),
    ],
)
@pytest.mark.parametrize(
    "module_path",
    [
        # fixme: must work by passing a module path without the model name
        "tests.fixtures.models:Group"
    ],
)
@pytest.mark.parametrize("depth", [None, 1, 2])
def test_run(
    temp_filename: Path,
    walker: WalkerChoice,
    decision: str,
    layout: LayoutChoice,
    module_path: str,
    format: Optional[FormatChoice],
    depth: Optional[int],
    file_loader: Callable[[str], Any],
) -> None:
    """
    ARRANGE a module path
        AND a filename
        AND a format
        AND a depth
    ACT run the driver
    ASSERT generates the expected file format
    """
    # arrange
    driver = Driver(walker, decision, layout)

    # act
    driver.run(module_path, temp_filename, format, depth)

    actual = temp_filename.read_text()

    # assert
    assert file_loader(actual)
