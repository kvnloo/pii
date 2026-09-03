from paw_pii.taxonomy import PII_TYPES, canonical_pii_type


def test_taxonomy_matches_pii_tracer_categories() -> None:
    assert PII_TYPES == (
        "private_person",
        "private_email",
        "private_phone",
        "private_address",
        "private_url",
        "private_date",
        "account_number",
        "secret",
        "other_pii",
    )


def test_ai4privacy_labels_map_to_canonical_types() -> None:
    assert canonical_pii_type("GIVENNAME1") == "private_person"
    assert canonical_pii_type("POSTCODE") == "private_address"
    assert canonical_pii_type("PASSPORT") == "account_number"
    assert canonical_pii_type("PASS") == "secret"
    assert canonical_pii_type("USERNAME") == "private_person"
    assert canonical_pii_type("IP") == "private_url"
    assert canonical_pii_type("nonsense") is None
