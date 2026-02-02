import argparse
import logging
from datetime import datetime


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sandbox entry point")
    parser.add_argument("--name", default="world", help="name to greet")
    parser.add_argument("--count", type=int, default=1, help="number of greetings (>= 1)")
    parser.add_argument("--quiet", action="store_true", help="suppress log output")
    return parser


def run(args: argparse.Namespace) -> int:
    if not args.quiet:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
        logging.info("Starting run")

    for i in range(args.count):
        message = f"Hello, {args.name}! ({i + 1}/{args.count})"
        print(message)

    if not args.quiet:
        logging.info("Finished at %s", datetime.now().isoformat(timespec="seconds"))

    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.count < 1:
        parser.error("--count must be >= 1")

    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
