#!/usr/bin/env python3
from pathlib import Path

import programasweights as paw

SPEC_PATH = Path(__file__).with_name("spec.txt")


def main() -> None:
    program = paw.compile(
        SPEC_PATH.read_text(encoding="utf-8").strip(),
        compiler="paw-ft-bs48",
        name="PII detector",
        tags=["pii", "privacy", "extraction"],
        public=True,
    )
    print(program.id)


if __name__ == "__main__":
    main()
