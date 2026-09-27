#!/usr/bin/env python3
"""Validate structured production release evidence."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - environment failure path
    yaml = None


PLACEHOLDERS = {"", "todo", "tbd", "n/a", "na", "none", "unknown", "-"}
RISK_LEVELS = {"low", "medium", "high", "critical"}
GATE_NAMES = {"code", "contract", "security", "data", "observability", "release"}
GATE_STATES = {"passed", "exception"}
ENVIRONMENTS = {"staging", "production"}
SEMVER = re.compile(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
COMMIT_SHA = re.compile(r"[0-9a-fA-F]{7,40}$")
ARTIFACT_DIGEST = re.compile(r"sha256:[0-9a-fA-F]{64}$")
HTTPS_URL = re.compile(r"https://[^\s]+$", re.IGNORECASE)
REPO_PATH = re.compile(r"(?:\.?\.?/)?[\w.@+-]+(?:/[\w.@+-]+)+$")
CHANGE_REF = re.compile(r"(?:PR|ISSUE|REQ|CHANGE)-\d+$", re.IGNORECASE)


def _mapping(value: Any, path: str, errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{path} must be an object")
        return {}
    return value


def _required_text(data: dict[str, Any], key: str, path: str, errors: list[str]) -> str:
    value = data.get(key)
    if not isinstance(value, str) or value.strip().lower() in PLACEHOLDERS:
        errors.append(f"{path}.{key} must be meaningful text")
        return ""
    return value.strip()


def _evidence_ref(value: str) -> bool:
    return bool(HTTPS_URL.fullmatch(value) or REPO_PATH.fullmatch(value))


def validate_release_evidence(data: Any, artifact_path: Path | None = None) -> list[str]:
    errors: list[str] = []
    root = _mapping(data, "root", errors)
    if root.get("schema_version") != 2:
        errors.append("schema_version must be 2")

    release = _mapping(root.get("release"), "release", errors)
    for key in ("id", "version", "environment", "owner", "change_ref", "commit_sha", "artifact_digest"):
        _required_text(release, key, "release", errors)
    version = str(release.get("version", "")).strip()
    if version and not SEMVER.fullmatch(version):
        errors.append("release.version must be semantic versioning")
    change_ref = str(release.get("change_ref", "")).strip()
    if change_ref and not (HTTPS_URL.fullmatch(change_ref) or CHANGE_REF.fullmatch(change_ref)):
        errors.append("release.change_ref must be HTTPS URL or PR/ISSUE/REQ/CHANGE-N")
    commit_sha = str(release.get("commit_sha", "")).strip()
    if commit_sha and not COMMIT_SHA.fullmatch(commit_sha):
        errors.append("release.commit_sha must be a 7-40 character hexadecimal commit SHA")
    artifact_digest = str(release.get("artifact_digest", "")).strip()
    if artifact_digest and not ARTIFACT_DIGEST.fullmatch(artifact_digest):
        errors.append("release.artifact_digest must be sha256:<64 hex characters>")
    if artifact_path is not None:
        if not artifact_path.is_file():
            errors.append(f"artifact file not found: {artifact_path}")
        else:
            actual_digest = f"sha256:{hashlib.sha256(artifact_path.read_bytes()).hexdigest()}"
            if artifact_digest and actual_digest.lower() != artifact_digest.lower():
                errors.append("release.artifact_digest does not match --artifact bytes")
    environment = str(release.get("environment", "")).strip().lower()
    if environment and environment not in ENVIRONMENTS:
        errors.append(f"release.environment must be one of {sorted(ENVIRONMENTS)}")
    approved_at = _required_text(release, "approved_at", "release", errors)
    if approved_at:
        try:
            parsed = dt.datetime.fromisoformat(approved_at.replace("Z", "+00:00"))
            if parsed.utcoffset() is None:
                errors.append("release.approved_at must include a timezone offset")
        except ValueError:
            errors.append("release.approved_at must be ISO-8601")
    rules_versions = _mapping(release.get("rules_versions"), "release.rules_versions", errors)
    if not rules_versions:
        errors.append("release.rules_versions must contain at least one package version")
    elif "common-governance" not in rules_versions:
        errors.append("release.rules_versions must include common-governance")
    for name, value in rules_versions.items():
        if not isinstance(name, str) or not isinstance(value, str) or not SEMVER.fullmatch(value):
            errors.append(f"release.rules_versions.{name} must be semantic versioning")

    artifact_trust = _mapping(root.get("artifact_trust"), "artifact_trust", errors)
    for key in ("sbom_ref", "provenance_ref", "signature_ref"):
        ref = _required_text(artifact_trust, key, "artifact_trust", errors)
        if ref and not _evidence_ref(ref):
            errors.append(f"artifact_trust.{key} must be HTTPS URL or repository path")
    _required_text(artifact_trust, "builder_id", "artifact_trust", errors)
    _required_text(artifact_trust, "verification_command", "artifact_trust", errors)
    verified_at = _required_text(artifact_trust, "verified_at", "artifact_trust", errors)
    if verified_at:
        try:
            parsed = dt.datetime.fromisoformat(verified_at.replace("Z", "+00:00"))
            if parsed.utcoffset() is None:
                errors.append("artifact_trust.verified_at must include a timezone offset")
        except ValueError:
            errors.append("artifact_trust.verified_at must be ISO-8601")

    requirements = root.get("requirements")
    if not isinstance(requirements, list) or not requirements:
        errors.append("requirements must contain at least one item")
    else:
        for index, item in enumerate(requirements):
            requirement = _mapping(item, f"requirements[{index}]", errors)
            _required_text(requirement, "id", f"requirements[{index}]", errors)
            evidence = _required_text(
                requirement,
                "acceptance_evidence",
                f"requirements[{index}]",
                errors,
            )
            if evidence and not _evidence_ref(evidence):
                errors.append(f"requirements[{index}].acceptance_evidence must be HTTPS URL or repository path")

    risk = _mapping(root.get("risk"), "risk", errors)
    level = _required_text(risk, "level", "risk", errors).lower()
    if level and level not in RISK_LEVELS:
        errors.append(f"risk.level must be one of {sorted(RISK_LEVELS)}")
    _required_text(risk, "summary", "risk", errors)
    if level in {"high", "critical"}:
        rollout = _required_text(risk, "rollout_evidence", "risk", errors)
        if rollout and not _evidence_ref(rollout):
            errors.append("risk.rollout_evidence must be HTTPS URL or repository path")

    rollback = _mapping(root.get("rollback"), "rollback", errors)
    if rollback.get("tested") is not True:
        errors.append("rollback.tested must be true")
    rollback_ref = _required_text(rollback, "command_or_runbook", "rollback", errors)
    if rollback_ref and " " not in rollback_ref and not _evidence_ref(rollback_ref):
        errors.append("rollback.command_or_runbook must be an executable command, HTTPS URL, or repository path")
    _required_text(rollback, "owner", "rollback", errors)

    observability = _mapping(root.get("observability"), "observability", errors)
    for key in ("dashboards", "alerts"):
        value = observability.get(key)
        if not isinstance(value, list) or not value:
            errors.append(f"observability.{key} must contain at least one item")
        elif any(not isinstance(item, str) or item.strip().lower() in PLACEHOLDERS for item in value):
            errors.append(f"observability.{key} contains an empty or placeholder item")
    window = observability.get("observation_window_minutes")
    if not isinstance(window, int) or isinstance(window, bool) or window < 60:
        errors.append("observability.observation_window_minutes must be an integer >= 60")

    gates = _mapping(root.get("gates"), "gates", errors)
    for name in sorted(GATE_NAMES):
        state = gates.get(name)
        if state not in GATE_STATES:
            errors.append(f"gates.{name} must be passed or exception")

    exceptions = root.get("exceptions")
    if not isinstance(exceptions, list):
        errors.append("exceptions must be an array")
    else:
        exception_gates = {name for name, state in gates.items() if state == "exception"}
        covered_gates: set[str] = set()
        for index, item in enumerate(exceptions):
            exception = _mapping(item, f"exceptions[{index}]", errors)
            for key in ("id", "owner", "compensating_controls"):
                _required_text(exception, key, f"exceptions[{index}]", errors)
            item_gates = exception.get("gates")
            if not isinstance(item_gates, list) or not item_gates:
                errors.append(f"exceptions[{index}].gates must contain at least one gate")
            else:
                unknown = {gate for gate in item_gates if gate not in GATE_NAMES}
                if unknown:
                    errors.append(f"exceptions[{index}].gates contains unknown gates: {sorted(unknown)}")
                covered_gates.update(gate for gate in item_gates if gate in GATE_NAMES)
            expires_at = _required_text(exception, "expires_at", f"exceptions[{index}]", errors)
            if expires_at:
                try:
                    expiry = dt.date.fromisoformat(expires_at)
                    if expiry < dt.date.today():
                        errors.append(f"exceptions[{index}].expires_at is expired")
                except ValueError:
                    errors.append(f"exceptions[{index}].expires_at must be YYYY-MM-DD")
        missing_exceptions = exception_gates - covered_gates
        if missing_exceptions:
            errors.append(f"exception gates lack approved exception records: {sorted(missing_exceptions)}")
        unused_exceptions = covered_gates - exception_gates
        if unused_exceptions:
            errors.append(f"exception records reference gates not in exception state: {sorted(unused_exceptions)}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate release-evidence.yaml")
    parser.add_argument("--file", type=Path, required=True)
    parser.add_argument("--artifact", type=Path, help="Artifact whose SHA-256 must match release.artifact_digest")
    parser.add_argument(
        "--require-artifact",
        action="store_true",
        help="Fail unless --artifact is supplied; recommended for production release CI",
    )
    args = parser.parse_args()
    if yaml is None:
        print("FAILED: PyYAML is required (pip install pyyaml)", file=sys.stderr)
        return 2
    if not args.file.is_file():
        print(f"FAILED: file not found: {args.file}", file=sys.stderr)
        return 1
    try:
        data = yaml.safe_load(args.file.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        print(f"FAILED: invalid YAML: {exc}", file=sys.stderr)
        return 1
    if args.require_artifact and args.artifact is None:
        print("FAILED: --require-artifact requires --artifact", file=sys.stderr)
        return 1
    errors = validate_release_evidence(data, args.artifact)
    if errors:
        print("FAILED:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print(f"OK: release evidence is complete: {args.file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
