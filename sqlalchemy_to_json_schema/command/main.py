import argparse

from magicalimport import import_symbol

from sqlalchemy_to_json_schema.types import LayoutChoice


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", help="the module or class to extract schemas from")
    parser.add_argument("--format", default=None, choices=["json", "yaml"])
    parser.add_argument(
        "--walker",
        choices=["noforeignkey", "foreignkey", "structural"],
        default="structural",
    )
    parser.add_argument("--decision", choices=["default", "useforeignkey"], default="default")
    parser.add_argument("--depth", default=None, type=int)
    parser.add_argument("--out", default=None, help="output to file")
    parser.add_argument(
        "--layout",
        choices=[layout.value for layout in LayoutChoice],
        default=LayoutChoice.SWAGGER_2.value,
    )
    parser.add_argument("--driver", default="sqlalchemy_to_json_schema.command.driver:Driver")
    args = parser.parse_args()

    driver_cls = import_symbol(args.driver, cwd=True)
    driver = driver_cls(args.walker, args.decision, LayoutChoice(args.layout))
    driver.run(args.target, args.out, format=args.format)
