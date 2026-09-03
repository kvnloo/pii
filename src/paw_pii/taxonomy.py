from __future__ import annotations

PII_TYPES = (
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

PII_TYPE_SET = frozenset(PII_TYPES)

PII_TYPE_ALIASES: dict[str, str] = {
    "private_name": "private_person",
    "private_username": "private_person",
    "private_ip": "private_url",
    "private_location": "private_address",
    "private_country": "private_address",
    "private_city": "private_address",
    "private_state": "private_address",
    "private_postcode": "private_address",
    "private_street": "private_address",
    "private_id": "account_number",
    "private_secret": "secret",
}


# The frozen benchmark uses ai4privacy's fine-grained labels. The demo uses the
# public PII-Tracer taxonomy so its output is easier to understand and compare.
AI4PRIVACY_TO_PII_TYPE: dict[str, str] = {
    "GIVENNAME1": "private_person",
    "GIVENNAME2": "private_person",
    "LASTNAME1": "private_person",
    "LASTNAME2": "private_person",
    "LASTNAME3": "private_person",
    "TITLE": "private_person",
    "EMAIL": "private_email",
    "TEL": "private_phone",
    "BUILDING": "private_address",
    "STREET": "private_address",
    "CITY": "private_address",
    "STATE": "private_address",
    "POSTCODE": "private_address",
    "COUNTRY": "private_address",
    "SECADDRESS": "private_address",
    "GEOCOORD": "private_address",
    "URL": "private_url",
    "BOD": "private_date",
    "DATE": "private_date",
    "TIME": "private_date",
    "IDCARD": "account_number",
    "PASSPORT": "account_number",
    "DRIVERLICENSE": "account_number",
    "SOCIALNUMBER": "account_number",
    "ACCOUNTNUMBER": "account_number",
    "BANKACCOUNT": "account_number",
    "CARDNUMBER": "account_number",
    "PASS": "secret",
    "PASSWORD": "secret",
    "TOKEN": "secret",
    "SEX": "other_pii",
    # PII-Tracer empirically groups usernames with people and IP addresses
    # with URL/network identifiers on the frozen comparison corpus.
    "USERNAME": "private_person",
    "IP": "private_url",
}


def canonical_pii_type(label: str) -> str | None:
    """Return a canonical nine-way PII type, or None for an unknown label."""

    normalized = label.strip().lower()
    if normalized in PII_TYPE_SET:
        return normalized
    if normalized in PII_TYPE_ALIASES:
        return PII_TYPE_ALIASES[normalized]
    return AI4PRIVACY_TO_PII_TYPE.get(label.strip().upper())


def require_pii_type(label: str) -> str:
    canonical = canonical_pii_type(label)
    if canonical is None:
        raise ValueError(f"unknown PII label: {label}")
    return canonical
