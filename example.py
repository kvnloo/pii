#!/usr/bin/env python3
import json

import programasweights as paw

PROGRAM_ID = "73a0e38b8bbe3427cd1d"


def main() -> None:
    detect_pii = paw.function(PROGRAM_ID)
    text = "Name: Ada Lovelace\nEmail: ada@example.com\nPIN: 4821"
    result = json.loads(detect_pii(text))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
