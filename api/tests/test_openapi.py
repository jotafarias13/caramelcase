"""The OpenAPI schema, and the copy of it the web app's types come from."""

import json
from pathlib import Path

from tests.support.commands import cli, output_of

REPO_DIR = Path(__file__).resolve().parents[2]
SCHEMA_FILE = REPO_DIR / "web" / "src" / "api" / "openapi.json"

V1_ROUTES = {
    ("post", "/auth/guest"),
    ("get", "/auth/google/start"),
    ("get", "/auth/google/callback"),
    ("post", "/auth/magic-link"),
    ("post", "/auth/magic-link/verify"),
    ("post", "/auth/logout"),
    ("get", "/me"),
    ("patch", "/me/settings"),
    ("get", "/me/export"),
    ("delete", "/me"),
    ("get", "/config"),
    ("get", "/subjects"),
    ("get", "/subjects/{slug}"),
    ("post", "/sessions"),
    ("post", "/sessions/{session_id}/answers"),
    ("post", "/sessions/{session_id}/finish"),
    ("get", "/sessions/{session_id}"),
    ("get", "/me/stats"),
    ("get", "/me/activity"),
    ("post", "/questions/{question_id}/report"),
    ("post", "/events"),
    ("get", "/health"),
}


def _schema_of_the_app() -> str:
    """What `make types` writes: the schema, from a process of its own,
    so that routes other tests add to the app are not in it.
    """
    result = cli("openapi", database_url="postgresql+asyncpg://unused/unused")
    assert result.returncode == 0, output_of(result)
    return result.stdout


def test_the_committed_schema_is_the_apps() -> None:
    committed = SCHEMA_FILE.read_text(encoding="utf-8")

    assert committed == _schema_of_the_app(), (
        "web/src/api/openapi.json is out of date: run `make types`"
    )


def test_every_v1_route_of_the_spec_is_in_the_schema_under_api_v1() -> None:
    schema = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))

    routes = {
        (method, path.removeprefix("/api/v1"))
        for path, operations in schema["paths"].items()
        for method in operations
    }

    assert all(path.startswith("/api/v1/") for path in schema["paths"])
    assert routes == V1_ROUTES


def test_every_route_documents_its_response_and_the_error_shape() -> None:
    schema = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
    error = {"$ref": "#/components/schemas/ErrorResponse"}

    for path, operations in schema["paths"].items():
        for method, operation in operations.items():
            where = f"{method} {path}"
            responses = operation["responses"]
            success = next(code for code in responses if code < "400")
            if success == "200":
                body = responses["200"]["content"]["application/json"]
                assert "$ref" in body["schema"], where
            assert responses["422"]["content"]["application/json"] == {
                "schema": error
            }, where


def test_the_session_payload_has_no_field_for_the_answers() -> None:
    schemas = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))[
        "components"
    ]["schemas"]

    def fields(name: str, seen: set[str]) -> set[str]:
        """Every field of a schema and of the schemas it refers to."""
        if name in seen:
            return set()
        seen.add(name)
        properties = schemas[name].get("properties", {})
        found = set(properties)
        for ref in _refs(properties):
            found |= fields(ref, seen)
        return found

    session_fields = fields("SessionResponse", set())
    answer_fields = fields("AnswerResponse", set())

    secret = {"correct_key", "reasons", "reason", "explanation"}
    assert not session_fields & secret
    assert secret <= answer_fields


def _refs(value: object) -> set[str]:
    if isinstance(value, dict):
        found = set()
        for key, inner in value.items():
            if key == "$ref":
                found.add(str(inner).rsplit("/", 1)[-1])
            else:
                found |= _refs(inner)
        return found
    if isinstance(value, list):
        return set().union(*(_refs(item) for item in value))
    return set()
