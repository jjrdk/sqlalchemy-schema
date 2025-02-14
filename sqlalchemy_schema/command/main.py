from collections.abc import Sequence
from pathlib import Path
from typing import Final, Optional

import click

from sqlalchemy_schema.command.driver import Driver
from sqlalchemy_schema.types import Decision, Format, Layout, Walker

DEFAULT_WALKER: Final = Walker.STRUCTURAL
DEFAULT_DECISION: Final = Decision.DEFAULT
DEFAULT_LAYOUT: Final = Layout.SWAGGER_2


@click.command()
@click.option("--format", type=click.Choice([format.value for format in Format]))
@click.option(
    "--walker",
    type=click.Choice([walker.value for walker in Walker]),
    default=DEFAULT_WALKER.value,
)
@click.option(
    "--decision",
    type=click.Choice([decision.value for decision in Decision]),
    default=DEFAULT_DECISION.value,
)
@click.option(
    "--layout",
    type=click.Choice([layout.value for layout in Layout]),
    default=DEFAULT_LAYOUT.value,
)
@click.option(
    "--out",
    type=click.Path(
        file_okay=True, dir_okay=False, resolve_path=True, writable=True, path_type=Path
    ),
)
@click.argument("targets", type=str, nargs=-1)
def main(
    targets: Sequence[str],
    walker: str,
    decision: str,
    layout: str,
    out: Optional[Path] = None,
    format: Optional[str] = None,
) -> None:
    driver = Driver(Walker(walker), Decision(decision), Layout(layout))
    driver.run(targets, filename=out, format=None if format is None else Format(format))


if __name__ == "__main__":
    main()
