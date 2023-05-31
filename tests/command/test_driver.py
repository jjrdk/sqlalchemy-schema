import json
from functools import partial
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Callable, Optional

import pytest
import yaml
from yaml import Loader

from sqlalchemy_to_json_schema.command.driver import Driver


@pytest.fixture
def temp_filename() -> Path:
    with NamedTemporaryFile() as f:
        yield Path(f.name)


@pytest.mark.parametrize("walker", ["noforeignkey", "foreignkey", "structural"])
@pytest.mark.parametrize("decision", ["default", "useforeignkey"])
@pytest.mark.parametrize("layout", ["swagger2.0", "jsonschema", "openapi3.0", "openapi2.0"])
@pytest.mark.parametrize(
    "format, file_loader",
    [
        pytest.param("json", json.loads),
        pytest.param("yaml", partial(yaml.load, Loader=Loader)),
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
    walker: str,
    decision: str,
    layout: str,
    module_path: str,
    format: str,
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
