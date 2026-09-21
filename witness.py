#!/usr/bin/env python3
"""Offline, dependency-free witness for two recorded MCP tool catalogs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


TOP_LEVEL_KEYS = {"protocolEra", "tools"}
TOOL_KEYS = {"name", "description", "inputSchema", "outputSchema", "annotations"}


class SnapshotError(ValueError):
    """A snapshot is malformed or does not contain enough evidence."""


def _canonical(value: Any) -> str:
    """Serialize JSON without changing array order or silently dropping keys."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise SnapshotError(f"cannot read JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise SnapshotError("snapshot must be a JSON object")
    return value


def _validate(snapshot: dict[str, Any]) -> dict[str, Any]:
    unknown = sorted(set(snapshot) - TOP_LEVEL_KEYS)
    if unknown:
        raise SnapshotError(f"unsupported top-level field: {unknown[0]}")
    protocol = snapshot.get("protocolEra")
    if not isinstance(protocol, str) or not protocol:
        raise SnapshotError("protocolEra must be a non-empty string")
    tools = snapshot.get("tools")
    if not isinstance(tools, list):
        raise SnapshotError("tools must be an array")

    normalized: list[dict[str, Any]] = []
    names: set[str] = set()
    for index, tool in enumerate(tools):
        if not isinstance(tool, dict):
            raise SnapshotError(f"tools[{index}] must be an object")
        unknown = sorted(set(tool) - TOOL_KEYS)
        if unknown:
            raise SnapshotError(f"tools[{index}] has unsupported field: {unknown[0]}")
        name = tool.get("name")
        if not isinstance(name, str) or not name:
            raise SnapshotError(f"tools[{index}].name must be a non-empty string")
        if name in names:
            raise SnapshotError(f"duplicate tool name: {name}")
        names.add(name)
        input_schema = tool.get("inputSchema")
        if not isinstance(input_schema, dict):
            raise SnapshotError(f"tools[{index}].inputSchema must be an object")
        if "description" in tool and not isinstance(tool["description"], str):
            raise SnapshotError(f"tools[{index}].description must be a string")
        for field in ("outputSchema", "annotations"):
            if field in tool and not isinstance(tool[field], dict):
                raise SnapshotError(f"tools[{index}].{field} must be an object")
        normalized.append(dict(tool))

    # Sorting is explicit: catalog ordering is not treated as a contract change.
    normalized.sort(key=lambda item: item["name"])
    return {"protocolEra": protocol, "tools": normalized}


def _parts(snapshot: dict[str, Any]) -> dict[str, str]:
    tools = snapshot["tools"]
    identity = [{"name": tool["name"]} for tool in tools]
    inputs = [{"name": tool["name"], "inputSchema": tool["inputSchema"]} for tool in tools]
    outputs = [
        {"name": tool["name"], "outputSchema": tool.get("outputSchema")}
        for tool in tools
    ]
    metadata = [
        {
            "name": tool["name"],
            "description": tool.get("description"),
            "annotations": tool.get("annotations"),
        }
        for tool in tools
    ]
    # The full catalog digest catches a valid, newly introduced field only if the
    # schema is updated to allow it; unknown fields fail closed in _validate.
    catalog = {"protocolEra": snapshot["protocolEra"], "tools": tools}
    return {
        "identity": _digest(identity),
        "input_schema": _digest(inputs),
        "output_schema": _digest(outputs),
        "metadata": _digest(metadata),
        "catalog": _digest(catalog),
    }


def compare(before_path: Path, after_path: Path) -> dict[str, Any]:
    try:
        before = _validate(_load(before_path))
        after = _validate(_load(after_path))
    except SnapshotError as exc:
        return {"state": "unknown", "reason": str(exc), "changed_dimensions": []}

    before_parts = _parts(before)
    after_parts = _parts(after)
    changed = [key for key in ("identity", "input_schema", "output_schema", "metadata", "catalog") if before_parts[key] != after_parts[key]]
    state = "current" if not changed else "changed"
    if before["protocolEra"] != after["protocolEra"]:
        state = "incompatible"
        changed.insert(0, "protocol_era")

    return {
        "state": state,
        "protocol_era": {"before": before["protocolEra"], "after": after["protocolEra"]},
        "changed_dimensions": changed,
        "before": before_parts,
        "after": after_parts,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    args = parser.parse_args()
    print(json.dumps(compare(args.before, args.after), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
