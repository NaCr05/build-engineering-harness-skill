from __future__ import annotations

import argparse


def greet(name: str) -> str:
    return f"Hello, {name.strip()}!"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    args = parser.parse_args()
    print(greet(args.name))


if __name__ == "__main__":
    main()
