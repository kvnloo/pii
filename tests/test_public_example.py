import hashlib
from pathlib import Path

from example import PROGRAM_ID

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PROGRAM_ID = "73a0e38b8bbe3427cd1d"
EXPECTED_SPEC_SHA256 = "376fae3801e2e23543ae11922fc70baf4e2906a8349658cdf681477fd3fd04e4"


def test_public_program_id_is_frozen_winner() -> None:
    assert PROGRAM_ID == EXPECTED_PROGRAM_ID


def test_root_spec_matches_compiled_winner() -> None:
    canonical = (ROOT / "spec.txt").read_text(encoding="utf-8").strip()
    benchmark_copy = (
        ROOT / "specs" / "pii-detector-typed-ft-v1.txt"
    ).read_text(encoding="utf-8").strip()
    assert canonical == benchmark_copy
    assert hashlib.sha256(canonical.encode()).hexdigest() == EXPECTED_SPEC_SHA256
