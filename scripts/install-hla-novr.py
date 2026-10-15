#!/usr/bin/env python3
"""Install or remove the pinned Half-Life: Alyx NoVR file overlay."""

import argparse
import hashlib
import json
import shutil
from pathlib import Path


STATE_NAME = ".dg-hla-novr"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def state_paths(game: Path) -> tuple[Path, Path]:
    state = game / STATE_NAME
    return state, state / "manifest.json"


def install(source: Path, game: Path, revision: str) -> bool:
    state, manifest_path = state_paths(game)
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        if manifest["revision"] != revision:
            raise ValueError("A different NoVR revision is installed; revert it first")
        repair = []
        for item in manifest["files"]:
            target = game / item["path"]
            if target.is_file() and digest(target) == item["sha256"]:
                continue
            if target.is_symlink() or (target.exists() and not target.is_file()):
                raise ValueError(f"Installed NoVR file changed: {target}")
            if item["original"]:
                if not target.is_file() or digest(target) != item["original_sha256"]:
                    raise ValueError(f"Installed NoVR file changed: {target}")
            elif target.exists():
                raise ValueError(f"Installed NoVR file changed: {target}")
            repair.append(item)
        for item in repair:
            relative = Path(item["path"])
            target = game / relative
            if digest(source / relative) != item["sha256"]:
                raise ValueError(f"Cached NoVR source changed: {source / relative}")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source / relative, target)
        return bool(repair)
    if state.exists() and any(state.iterdir()):
        raise ValueError(f"Unrecognized installation state: {state}")
    if not (game / "hlvr" / "gameinfo.gi").is_file():
        raise ValueError(f"Half-Life: Alyx game directory not found: {game}")
    files = sorted(p for p in source.rglob("*") if p.is_file())
    if not files or any(p.is_symlink() for p in files):
        raise ValueError("NoVR source is empty or contains symlinks")
    records = []
    for path in files:
        relative = path.relative_to(source)
        target = game / relative
        if target.exists() and not target.is_file():
            raise ValueError(f"NoVR would replace a non-file: {target}")
        if target.is_symlink():
            raise ValueError(f"NoVR would replace a symlink: {target}")
        records.append({
            "path": relative.as_posix(),
            "sha256": digest(path),
            "original": target.exists(),
            "original_sha256": digest(target) if target.exists() else None,
        })
    state.mkdir(exist_ok=True)
    for item in records:
        if item["original"]:
            relative = Path(item["path"])
            backup = state / "original" / relative
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(game / relative, backup)
    # Publish the manifest before copying: an interrupted install can be
    # reverted, with backups already complete.
    manifest_path.write_text(json.dumps({"revision": revision, "files": records}, indent=2) + "\n")
    for item in records:
        relative = Path(item["path"])
        target = game / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / relative, target)
    return True


def revert(game: Path) -> bool:
    state, manifest_path = state_paths(game)
    if not manifest_path.exists():
        return False
    manifest = json.loads(manifest_path.read_text())
    for item in manifest["files"]:
        target = game / item["path"]
        if target.exists():
            expected = {item["sha256"]}
            if item["original"]:
                expected.add(item["original_sha256"])
            if not target.is_file() or digest(target) not in expected:
                raise ValueError(f"Refusing to overwrite a changed file: {target}")
        elif item["original"]:
            raise ValueError(f"Original game file is missing: {target}")
    for item in reversed(manifest["files"]):
        relative = Path(item["path"])
        target = game / relative
        if item["original"]:
            shutil.copy2(state / "original" / relative, target)
        else:
            target.unlink(missing_ok=True)
            parent = target.parent
            while parent != game:
                try:
                    parent.rmdir()
                except OSError:
                    break
                parent = parent.parent
    shutil.rmtree(state)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game", required=True, type=Path)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--revision")
    parser.add_argument("--revert", action="store_true")
    args = parser.parse_args()
    if args.revert:
        changed = revert(args.game)
    else:
        if not args.source or not args.revision:
            parser.error("--source and --revision are required for installation")
        changed = install(args.source, args.game, args.revision)
    print(f"changed: {str(changed).lower()}")


if __name__ == "__main__":
    main()
