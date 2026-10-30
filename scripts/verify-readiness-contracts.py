"""Validate candidate schemas/seeds and structural examples; no cloud access."""
import copy
import json
from decimal import Decimal
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "docs/api/schemas"
SCHEMA = json.loads((DIRECTORY / "stage-2.schema.json").read_text(encoding="utf-8"), parse_float=Decimal)
SEEDS = json.loads((DIRECTORY / "stage-2-seed-proposal.json").read_text(encoding="utf-8"), parse_float=Decimal)


def validator(name):
    return Draft202012Validator(
        {"$schema": SCHEMA["$schema"], "$defs": SCHEMA["$defs"],
         "$ref": f"#/$defs/{name}"}, format_checker=FormatChecker()
    )


def main():
    Draft202012Validator.check_schema(SCHEMA)
    validator("SeedCatalogue").validate(SEEDS)
    definitions = SEEDS["definitions"]
    ids = [item["parameterDefinitionId"] for item in definitions]
    assert len(ids) == len(set(ids)), "Seed IDs must be unique"
    assert {item["family"] for item in definitions} == {
        "pH", "ammonia", "nitrite", "nitrate", "phosphate", "calcium",
        "magnesium", "alkalinity"
    }
    for definition in definitions:
        codes = [unit["unitCode"] for unit in definition["allowedUnits"]]
        assert len(codes) == len(set(codes)), "Unit codes must be unique per definition"
        assert "ppm" not in codes
        for unit in definition["allowedUnits"]:
            assert unit.get("minimum", -1000000) <= unit.get("maximum", 1000000)

    reading = {
        "parameterDefinitionId": ids[0], "definitionRevision": 1,
        "value": 7.25, "unitCode": "pH", "qualifier": "exact"
    }
    panel = {"measuredAt": "2026-10-29T12:00:00+11:00", "readings": [reading]}
    tank = {"name": "Synthetic freshwater tank", "waterType": "freshwater",
            "timezone": "Australia/Sydney"}
    cases = []

    def case(name, schema, value, expected=True):
        cases.append((name, schema, value, expected))

    for system in ["metric", "usCustomary", "ukImperial"]:
        case(system, "ProfileUpdate", {"measurementSystem": system})
    case("profile missing explicit choice", "ProfileUpdate", {}, False)
    case("incomplete profile read", "Profile", {"completed": False})
    case("completed profile read", "Profile", {"completed": True, "measurementSystem": "metric"})
    case("completed profile needs explicit choice", "Profile", {"completed": True}, False)
    case("unknown preference", "ProfileUpdate", {"measurementSystem": "imperial"}, False)
    case("tank without optional volume", "TankCreate", tank)
    for code in ["L", "gal-US", "gal-UK"]:
        case(code, "TankCreate", {**tank, "operatingWaterVolume": {"value": 100, "unitCode": code}})
    case("owner injection", "TankCreate", {**tank, "ownerId": ids[0]}, False)
    case("empty tank name", "TankCreate", {**tank, "name": "   "}, False)
    case("zero volume", "Volume", {"value": 0, "unitCode": "L"}, False)
    case("ambiguous gallon", "Volume", {"value": 1, "unitCode": "gal"}, False)
    case("panel", "PanelCreate", panel)
    case("offset required", "PanelCreate", {**panel, "measuredAt": "2026-10-29T12:00:00"}, False)
    case("invalid date", "PanelCreate", {**panel, "measuredAt": "2026-02-30T12:00:00Z"}, False)
    case("empty readings", "PanelCreate", {**panel, "readings": []}, False)
    case("50 readings structural bound", "PanelCreate", {**panel, "readings": [reading] * 50})
    case("51 readings", "PanelCreate", {**panel, "readings": [reading] * 51}, False)
    case("unknown request field", "PanelCreate", {**panel, "ownerId": ids[0]}, False)
    case("notes limit", "PanelCreate", {**panel, "notes": "x" * 4001}, False)
    case("method limit", "PanelCreate", {**panel, "testMethod": "x" * 201}, False)
    case("positive revision", "ReadingInput", {**reading, "definitionRevision": 0}, False)
    case("GUID required", "ReadingInput", {**reading, "parameterDefinitionId": "nitrate"}, False)
    case("numeric value required", "ReadingInput", {**reading, "value": "7.25"}, False)
    case("numeric envelope", "ReadingInput", {**reading, "value": 1000001}, False)
    case("precision envelope", "ReadingInput", {**reading, "value": 0.0000001}, False)
    case("limit qualifier", "ReadingInput", {**reading, "qualifier": "belowDetectionLimit"})
    saved = {**panel, "id": ids[0], "tankId": ids[1],
             "recordedAt": "2026-10-29T01:00:01Z", "revision": 1}
    case("server response fields", "Panel", saved)
    case("UTC server output", "Panel", {**saved, "recordedAt": "2026-10-29T12:00:01+11:00"}, False)
    case("response fields rejected in request", "PanelCreate", saved, False)
    case("empty selection before entry", "SelectionUpdate", {"parameterDefinitionIds": []})
    case("duplicate selection", "SelectionUpdate", {"parameterDefinitionIds": [ids[0], ids[0]]}, False)
    pairs = [{"parameterDefinitionId": ids[0], "definitionRevision": 1}]
    case("batch request", "ValidationRequest", {"definitions": pairs})
    case("no reading values in batch", "ValidationRequest", {"definitions": [reading]}, False)
    context = {"tankId": ids[1], "profileCompleted": True, "definitions": [definitions[0]]}
    case("authoritative context", "ValidationContext", context)
    case("incomplete profile cannot be success", "ValidationContext", {**context, "profileCompleted": False}, False)
    problem = {"type": "about:blank", "title": "Invalid reading", "status": 422,
               "code": "invalid-reading", "traceId": "synthetic-trace"}
    case("safe problem", "Problem", problem)
    case("internal exception rejected", "Problem", {**problem, "exception": "private"}, False)
    for name, schema, value, expected in cases:
        value = json.loads(json.dumps(copy.deepcopy(value)), parse_float=Decimal)
        errors = list(validator(schema).iter_errors(value))
        if (not errors) != expected:
            raise AssertionError(f"{name}: expected valid={expected}; {errors}")
    print(f"PASS: schema meta-validation, 12 accepted seed shapes, {len(cases)} structural cases")
    print("NOT VERIFIED: runtime decimal parsing, identity, ownership, duplicates in panels,")
    print("definition eligibility, IANA zones, clock bounds, payload bytes or Azure behaviour.")


if __name__ == "__main__":
    main()
