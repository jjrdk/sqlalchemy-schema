import json
from collections.abc import Iterator, Sequence
from functools import partial
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Callable, Optional
from unittest.mock import ANY

import pytest
import yaml
from pytest_mock import MockerFixture
from yaml import Loader

from sqlalchemy_schema.command.driver import Driver
from sqlalchemy_schema.command.main import (
    DEFAULT_DECISION,
    DEFAULT_LAYOUT,
    DEFAULT_WALKER,
)
from sqlalchemy_schema.types import Decision, Format, Layout, Walker


@pytest.fixture
def temp_filename() -> Iterator[Path]:
    with NamedTemporaryFile() as f:
        yield Path(f.name)


class TestDriver:
    @pytest.mark.parametrize("walker", Walker)
    @pytest.mark.parametrize("decision", Decision)
    @pytest.mark.parametrize("layout", Layout)
    @pytest.mark.parametrize(
        "format, file_loader",
        [
            pytest.param(None, json.loads),
            pytest.param(Format.JSON, json.loads),
            pytest.param(Format.YAML, partial(yaml.load, Loader=Loader)),
        ],
    )
    @pytest.mark.parametrize(
        "targets",
        [
            ["tests.fixtures.models.user"],
            ["tests.fixtures.models.user:Group"],
        ],
    )
    @pytest.mark.parametrize("depth", [None, 1, 2])
    def test_run(
        self,
        temp_filename: Path,
        walker: Walker,
        decision: Decision,
        layout: Layout,
        targets: Sequence[str],
        format: Optional[Format],
        depth: Optional[int],
        file_loader: Callable[[str], Any],
    ) -> None:
        """
        ARRANGE a list of targets
            AND a filename
            AND a format
            AND a depth
        ACT run the driver
        ASSERT generates the expected file format
        """
        # arrange
        driver = Driver(walker, decision, layout)

        # act
        driver.run(targets, filename=temp_filename, format=format, depth=depth)

        actual = temp_filename.read_text()

        # assert
        assert file_loader(actual)

    @pytest.mark.parametrize(
        "targets",
        [
            [
                "tests.fixtures.models.user",
                "tests.fixtures.models.user:Group",
            ]
        ],
    )
    def test_run_no_filename(self, mocker: MockerFixture, targets: Sequence[str]) -> None:
        """
        ARRANGE a list of targets
            AND default parameters
            AND no output filename
        ACT run the driver
        ASSERT generates the expected file format on the stdout
        """
        # arrange
        driver = Driver(DEFAULT_WALKER, DEFAULT_DECISION, DEFAULT_LAYOUT)

        m_stdout = mocker.patch(
            "sqlalchemy_schema.command.driver.sys.stdout", autospec=True
        )

        # act
        driver.run(targets)

        # assert
        m_stdout.write.assert_called()

    @pytest.mark.parametrize(
        "targets, expected",
        [
            pytest.param(
                ["tests.fixtures.models.user:Group"],
                {"definitions": {"Group": ANY}},
                id="Single model",
            ),
            pytest.param(
                ["tests.fixtures.models.user"],
                {"definitions": {"Group": ANY, "User": ANY}},
                id="Single module",
            ),
            pytest.param(
                ["tests.fixtures.models.user", "tests.fixtures.models.address"],
                {"definitions": {"Group": ANY, "User": ANY, "Address": ANY}},
                id="Multiple modules",
            ),
            pytest.param(
                ["tests.fixtures.models.user:Group", "tests.fixtures.models.address"],
                {"definitions": {"Group": ANY, "Address": ANY}},
                id="Mix of module and model",
            ),
        ],
    )
    def test_run_multiple_targets(
        self, targets: Sequence[str], temp_filename: Path, expected: dict[str, Any]
    ) -> None:
        """
        ARRANGE a list of targets
            AND default parameters
            AND no output filename
        ACT run the driver
        ASSERT generates the expected file format on the stdout
        """
        # arrange
        driver = Driver(Walker.NOFOREIGNKEY, DEFAULT_DECISION, DEFAULT_LAYOUT)

        # act
        driver.run(targets, filename=temp_filename)

        actual = temp_filename.read_text()

        # assert
        assert json.loads(actual) == expected
