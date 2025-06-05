import yaml

OPENAPI_PATH = "./prometeo_mcp/docs/validation.yml"


SCHEMA_MAP = {
    "account_number": "AccountNumber",
    "document_number": "DocumentNumber",
    "document_type": "DocumentType",
    "account_type": "AccountType",
    "bank_code": "BankCode",
    "branch_code": "BranchCode",
    "country_code": "Country",
}


def get_param_description(parameter: str) -> str | None:
    """Extract the description for a schema from an OpenAPI YAML file."""
    with open(OPENAPI_PATH, "r") as f:
        spec = yaml.safe_load(f)

    schema_name = SCHEMA_MAP.get(parameter)
    if not schema_name:
        return None

    return (
        spec.get("components", {})
        .get("schemas", {})
        .get(schema_name, {})
        .get("description")
    )
