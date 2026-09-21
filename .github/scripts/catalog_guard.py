#!/usr/bin/env python3
"""Trusted validation and promotion helpers for declarative Pi-MFX preset manifests."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import re
import sys
import urllib.parse
import urllib.request

from jsonschema import Draft202012Validator

ROOT = pathlib.Path(__file__).resolve().parents[2]
MAX_MANIFEST_BYTES = 1024 * 1024
MAX_NODES = 20000
MAX_DEPTH = 32
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{2,63}$")
ATTACHMENT_RE = re.compile(
    r"https://github\.com/user-attachments/files/[0-9]+/[A-Za-z0-9._%()-]+\.json"
)
BLOCKED_TEXT = (
    "javascript:",
    "data:",
    "file:",
    "<script",
    "</script",
    "<html",
    "<svg",
    "#!/",
    "powershell",
    "cmd.exe",
    "/bin/sh",
    "onerror=",
)


class GuardError(RuntimeError):
    pass


def load_json(path: pathlib.Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise GuardError(f"{path}: invalid JSON: {exc}") from exc


def walk(value, depth=0):
    if depth > MAX_DEPTH:
        raise GuardError("manifest nesting is too deep")
    yield value
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from walk(item, depth + 1)
    elif isinstance(value, list):
        for item in value:
            yield from walk(item, depth + 1)


def validate_manifest(data, source="manifest"):
    schema = load_json(ROOT / "schema/preset-package-v2.schema.json")
    errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda item: list(item.path))
    if errors:
        detail = "; ".join(f"{error.json_path}: {error.message}" for error in errors[:8])
        raise GuardError(f"{source}: schema validation failed: {detail}")

    values = list(walk(data))
    if len(values) > MAX_NODES:
        raise GuardError(f"{source}: manifest contains too many values")

    rendered = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    if len(rendered.encode("utf-8")) > MAX_MANIFEST_BYTES:
        raise GuardError(f"{source}: manifest exceeds 1 MiB")

    lowered = rendered.lower()
    for marker in BLOCKED_TEXT:
        if marker in lowered:
            raise GuardError(f"{source}: script-like or active content is forbidden")

    for value in values:
        if not isinstance(value, str):
            continue
        if "\x00" in value or "../" in value or "..\\" in value:
            raise GuardError(f"{source}: unsafe string or path traversal")
        if len(value) > 65536:
            raise GuardError(f"{source}: string value is too long")

    allowed_uris = []
    for slot in data.get("preset", {}).get("chain", []):
        allowed_uris.append(slot.get("uri", ""))
    for effect in data.get("dependencies", {}).get("effects", []):
        allowed_uris.append(effect.get("uri", ""))

    without_uris = rendered
    for uri in sorted({uri for uri in allowed_uris if uri}, key=len, reverse=True):
        without_uris = without_uris.replace(json.dumps(uri, ensure_ascii=False)[1:-1], "")
    if re.search(r"https?://", without_uris, re.IGNORECASE):
        raise GuardError(f"{source}: arbitrary URLs outside trusted LV2 URI fields are forbidden")

    if data.get("previews"):
        raise GuardError(f"{source}: preview media is not accepted; submissions are JSON only")

    for group in ("tone3000", "irs", "localAssets"):
        for asset in data.get("dependencies", {}).get(group, []):
            filename = asset.get("expectedFilename", "")
            if not filename or filename in {".", ".."} or ".." in filename:
                raise GuardError(f"{source}: unsafe asset filename")

    if data.get("license") != "MIT":
        raise GuardError(f"{source}: preset manifests must use the MIT license")
    if data.get("dependencies", {}).get("irs") or data.get("dependencies", {}).get("localAssets"):
        raise GuardError(f"{source}: every NAM and IR must use a trusted TONE3000 reference")
    for slot in data.get("preset", {}).get("chain", []):
        uri = slot.get("uri", "")
        for filename in slot.get("state", {}).get("properties", {}).values():
            folded = str(filename).lower()
            if folded.endswith(".nam") and uri != "http://two-play.com/plugins/toob-nam":
                raise GuardError(f"{source}: NAM files must use TooB Neural Amp Modeler")
            if folded.endswith(".wav") and uri != "http://two-play.com/plugins/toob-cab-ir":
                raise GuardError(f"{source}: cabinet IR files must use TooB Cab IR")

    return data


def compact_sha256(data):
    compact = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(compact).hexdigest()


def content_fingerprint(data):
    identity = json.loads(json.dumps(data))
    for key in ("id", "name", "author", "description", "tags", "license", "checksums", "previews"):
        identity.pop(key, None)
    preset = identity.get("preset", {})
    preset.pop("name", None)
    preset.pop("author", None)
    return compact_sha256(identity)


def normalized_name(value):
    return " ".join(str(value).split()).casefold()


def validate_catalog():
    failures = []
    presets_root = ROOT / "presets"
    if presets_root.exists():
        for path in presets_root.rglob("*"):
            if path.is_symlink():
                failures.append(f"{path.relative_to(ROOT)}: symlinks are forbidden")
            elif path.is_file() and path.name != "manifest.json":
                failures.append(f"{path.relative_to(ROOT)}: only manifest.json is allowed")

    catalog = load_json(ROOT / "catalog/index.json")
    if catalog.get("format") != "pimfx-community-catalog" or catalog.get("formatVersion") != 2:
        failures.append("catalog/index.json: unsupported catalog format")

    indexed_paths = set()
    seen_ids = set()
    seen_names = set()
    seen_content = set()
    for entry in catalog.get("presets", []):
        preset_id = entry.get("id", "")
        manifest_path = entry.get("manifestPath", "")
        expected_path = f"presets/{preset_id}/manifest.json"
        if not ID_RE.fullmatch(preset_id) or preset_id in seen_ids:
            failures.append(f"catalog/index.json: invalid or duplicate id {preset_id!r}")
            continue
        seen_ids.add(preset_id)
        name_key = normalized_name(entry.get("name", ""))
        content_key = entry.get("contentSha256", "")
        if not name_key or name_key in seen_names:
            failures.append(f"catalog/index.json: duplicate preset name {entry.get('name')!r}")
        seen_names.add(name_key)
        if not re.fullmatch(r"[a-f0-9]{64}", content_key) or content_key in seen_content:
            failures.append(f"catalog/index.json: invalid or duplicate content fingerprint for {preset_id}")
        seen_content.add(content_key)
        if manifest_path != expected_path:
            failures.append(f"catalog/index.json: unsafe manifest path for {preset_id}")
            continue
        indexed_paths.add(manifest_path)
        path = ROOT / manifest_path
        if not path.is_file() or path.is_symlink():
            failures.append(f"{manifest_path}: indexed manifest is missing or unsafe")
            continue
        try:
            data = validate_manifest(load_json(path), manifest_path)
            if data.get("id") != preset_id:
                failures.append(f"{manifest_path}: manifest id does not match index")
            if entry.get("manifestSha256") != compact_sha256(data):
                failures.append(f"{manifest_path}: catalog checksum mismatch")
            if entry.get("contentSha256") != content_fingerprint(data):
                failures.append(f"{manifest_path}: catalog content fingerprint mismatch")
        except GuardError as exc:
            failures.append(str(exc))

    actual_paths = {
        path.relative_to(ROOT).as_posix()
        for path in presets_root.glob("*/manifest.json")
    } if presets_root.exists() else set()
    for unlisted in sorted(actual_paths - indexed_paths):
        failures.append(f"{unlisted}: manifest is not listed in catalog/index.json")

    if failures:
        raise GuardError("\n".join(failures))
    print("Catalog validation passed")


def issue_event(path):
    event = load_json(pathlib.Path(path))
    issue = event.get("issue", {})
    number = issue.get("number")
    body = issue.get("body") or ""
    if not isinstance(number, int) or number < 1:
        raise GuardError("issue event is missing a valid issue number")
    return event, number, body


def attachment_url(body):
    urls = list(dict.fromkeys(ATTACHMENT_RE.findall(body)))
    if len(urls) != 1:
        raise GuardError("submission must contain exactly one GitHub JSON attachment")
    parsed = urllib.parse.urlsplit(urls[0])
    if parsed.scheme != "https" or parsed.hostname != "github.com":
        raise GuardError("submission attachment must be hosted by GitHub")
    if not re.fullmatch(r"/user-attachments/files/[0-9]+/[A-Za-z0-9._%()-]+\.json", parsed.path):
        raise GuardError("submission attachment path is unsafe")
    return urls[0]


def download_manifest(url):
    request = urllib.request.Request(url, headers={"User-Agent": "Pi-MFX-Catalog-Guard/1"})
    with urllib.request.urlopen(request, timeout=20) as response:
        final = urllib.parse.urlsplit(response.geturl())
        if final.scheme != "https" or final.hostname not in {"github.com", "objects.githubusercontent.com"}:
            raise GuardError("GitHub attachment redirected to an untrusted host")
        declared = response.headers.get("Content-Length")
        if declared and int(declared) > MAX_MANIFEST_BYTES:
            raise GuardError("submission exceeds 1 MiB")
        raw = response.read(MAX_MANIFEST_BYTES + 1)
    if len(raw) > MAX_MANIFEST_BYTES:
        raise GuardError("submission exceeds 1 MiB")
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise GuardError(f"attachment is not valid UTF-8 JSON: {exc}") from exc


def manifest_from_issue(event_path):
    _, number, body = issue_event(event_path)
    data = validate_manifest(download_manifest(attachment_url(body)), f"issue #{number}")
    return number, data


def append_output(name, value):
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as handle:
            handle.write(f"{name}={value}\n")


def prepare_issue(event_path):
    issue_number, data = manifest_from_issue(event_path)
    preset_id = data["id"]
    if not ID_RE.fullmatch(preset_id):
        raise GuardError("preset id is unsafe")

    catalog_path = ROOT / "catalog/index.json"
    catalog = load_json(catalog_path)
    fingerprint = content_fingerprint(data)
    name_key = normalized_name(data.get("name", ""))
    for entry in catalog.get("presets", []):
        if entry.get("id") == preset_id:
            raise GuardError(f"catalog already contains preset id {preset_id}")
        if normalized_name(entry.get("name", "")) == name_key:
            raise GuardError("catalog already contains a preset with that name")
        if entry.get("contentSha256") == fingerprint:
            raise GuardError("catalog already contains that exact preset and settings")

    manifest_path = ROOT / "presets" / preset_id / "manifest.json"
    if manifest_path.exists():
        raise GuardError(f"preset path already exists for {preset_id}")
    manifest_path.parent.mkdir(parents=True, exist_ok=False)
    manifest_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    entry = {
        "id": preset_id,
        "name": data["name"],
        "author": data["author"],
        "description": data["description"],
        "tags": data["tags"],
        "license": data["license"],
        "minimumPiMfxVersion": data["compatibility"]["minimumPiMfxVersion"],
        "manifestPath": f"presets/{preset_id}/manifest.json",
        "manifestSha256": compact_sha256(data),
        "contentSha256": fingerprint,
    }
    catalog.setdefault("presets", []).append(entry)
    catalog["presets"].sort(key=lambda item: item["id"])
    catalog["updatedAt"] = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    catalog_path.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    validate_catalog()
    append_output("preset_id", preset_id)
    append_output("issue_number", str(issue_number))
    print(f"Prepared {preset_id} from issue #{issue_number}")


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate-catalog")
    issue = sub.add_parser("validate-issue")
    issue.add_argument("--event", required=True)
    prepare = sub.add_parser("prepare-issue")
    prepare.add_argument("--event", required=True)
    args = parser.parse_args()

    try:
        if args.command == "validate-catalog":
            validate_catalog()
        elif args.command == "validate-issue":
            number, data = manifest_from_issue(args.event)
            print(f"Issue #{number} manifest {data['id']} passed validation")
        elif args.command == "prepare-issue":
            prepare_issue(args.event)
    except GuardError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
