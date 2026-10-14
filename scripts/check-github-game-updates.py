#!/usr/bin/env python3
"""Report new GitHub releases for the PC games in the rendered OGM catalog."""

import os
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import yaml


ROOT = Path(__file__).resolve().parents[1]
DESKTOP_DIR = ROOT / "config/desktop/rendered"
VARS_DIR = ROOT / "ansible/group_vars/all"
GAME_CATEGORIES = {"port", "decomp", "recomp", "fangame", "wine", "arcade"}

# Values remain in group_vars; this only tells the sweep which pin to compare.
# Games built from a moving Git ref, or installed by a latest-release role, are
# still queried and shown as REVIEW rather than silently assumed current.
PIN_VARS = {
    "gaming-2ship2harkinian": ("2ship2harkinian.yml", "dg_two_ship2harkinian_version"),
    "gaming-banjotooie-recomp": ("banjotooie_recomp.yml", "dg_btooie_release_tag"),
    "gaming-beetle-recomp": ("beetle_recomp.yml", "dg_bar_version"),
    "gaming-cbfd-recomp": ("cbfd_recomp.yml", "dg_cbfd_version"),
    "gaming-dk64-recomp": ("dk64_recomp.yml", "dg_dk64_version"),
    "gaming-dkr-r": ("dkr_recomp.yml", "dg_dkr_release_tag"),
    "gaming-doom2-ray-traced": ("prboom_rt.yml", "dg_prboom_rt_version"),
    "gaming-ffvii-7th-heaven": ("7th_heaven.yml", "dg_7th_heaven_version"),
    "gaming-fzero": ("fzero_recomp.yml", "dg_fzero_release_tag"),
    "gaming-gdiffuser": ("gdiffuser.yml", "dg_gdiffuser_version"),
    "gaming-lighthouse": ("lighthouse.yml", "dg_lighthouse_version"),
    "gaming-midnightclubla": ("midnightclub_la.yml", "dg_mcla_release_tag"),
    "gaming-mph-recomp": ("mph_recomp.yml", "dg_mph_version"),
    "gaming-opensc2k": ("opensc2k.yml", "dg_opensc2k_version"),
    "gaming-perfect-dark": ("perfect_dark.yml", "dg_pd_release_tag"),
    "gaming-pilotwings-recomp": ("pilotwings_recomp.yml", "dg_pw64_version"),
    "gaming-roadrash64": ("roadrash64_recomp.yml", "dg_rr64_release_tag"),
    "gaming-ship-of-harkinian": ("ship_of_harkinian.yml", "dg_ship_of_harkinian_version"),
    "gaming-smb-remastered": ("smb_remastered.yml", "dg_smb_remastered_version"),
    "gaming-smw-remastered": ("smw_remastered.yml", "dg_smw_remastered_version"),
    "gaming-sonic3air": ("sonic3air.yml", "dg_s3air_version"),
    "gaming-spaghettikart": ("spaghettikart.yml", "dg_spaghettikart_version"),
    "gaming-starfox-enhanced": ("starfox_enhanced.yml", "dg_sfe_version"),
    "gaming-starship": ("starship.yml", "dg_starship_version"),
    "gaming-triaevum": ("triaevum.yml", "dg_triaevum_version"),
    "gaming-waverace-recomp": ("waverace_recomp.yml", "dg_wr64_release_tag"),
    "gaming-wipeout-pe": ("wipeout_pe.yml", "dg_wipeout_pe_version"),
    "gaming-wwhd-recomp": ("wwhd_recomp.yml", "dg_wwhd_release_tag"),
    "ridge-racer": ("ridge_racer.yml", "dg_ridge_racer_version"),
    "sega-rally-hd": ("sega_rally.yml", "dg_sega_rally_version"),
    "virtua-fighter": ("model1.yml", "dg_model1_vf_version"),
    "virtua-racing": ("model1.yml", "dg_model1_vr_version"),
}

# One repository publishes several unrelated games under separate tag prefixes.
TAG_PREFIXES = {
    "gaming-dkr-r": "Version",
    "gaming-midnightclubla": "midnightclubla-",
}


def catalog_games():
    games = []
    for desktop in sorted(DESKTOP_DIR.glob("*.desktop")):
        fields = {}
        for line in desktop.read_text().splitlines():
            if line.startswith("X-OGM-") and "=" in line:
                key, value = line.split("=", 1)
                fields[key] = value
        repo = fields.get("X-OGM-GitHub", "")
        if fields.get("X-OGM-Category") not in GAME_CATEGORIES or not repo:
            continue
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
            raise ValueError(f"Invalid GitHub repo in {desktop}: {repo}")
        games.append((desktop.stem, repo))
    return games


def pinned_tag(stem, var_cache):
    spec = PIN_VARS.get(stem)
    if spec is None:
        return None
    filename, key = spec
    if filename not in var_cache:
        var_cache[filename] = yaml.safe_load((VARS_DIR / filename).read_text())
    value = var_cache[filename].get(key)
    if value is None:
        raise ValueError(f"Cannot resolve {filename}:{key}")
    pin = re.sub(
        r"{{\s*(\w+)\s*}}",
        lambda match: str(var_cache[filename][match.group(1)]),
        str(value),
    )
    if "{{" in pin:
        raise ValueError(f"Cannot resolve {filename}:{key}")
    return pin


def github_token():
    token = os.environ.get("GITHUB_TOKEN", "")
    if re.fullmatch(r"(?:gh[opsur]_|github_pat_)[A-Za-z0-9_]+", token):
        return token
    if shutil.which("gh"):
        try:
            result = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, timeout=5)
        except subprocess.TimeoutExpired:
            return None
        if result.returncode == 0:
            lines = result.stdout.splitlines()
            token = lines[-1].strip() if lines else ""
            if re.fullmatch(r"(?:gh[opsur]_|github_pat_)[A-Za-z0-9_]+", token):
                return token
    return None


def latest_release(repo, stem, pin, token):
    url = f"https://api.github.com/repos/{repo}/releases?per_page=100"
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "distrobox-gaming-game-sweep"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with urlopen(Request(url, headers=headers), timeout=25) as response:
        import json

        releases = json.load(response)
    if not isinstance(releases, list):
        raise ValueError(f"Unexpected GitHub response for {repo}")
    prefix = TAG_PREFIXES.get(stem, "")
    matching = [r for r in releases if not r.get("draft") and r.get("tag_name", "").lower().startswith(prefix.lower())]
    if pin and re.match(r"^[vV]?\d", pin):
        matching = [r for r in matching if re.match(r"^[vV]?\d", r["tag_name"])]
    # A rolling nightly, devel, or test channel is not the successor to a
    # stable pin. Keep it visible through GitHub, but compare like with like.
    if pin and not any(word in pin.lower() for word in ("nightly", "devel", "test")):
        matching = [r for r in matching if not any(word in r["tag_name"].lower() for word in ("nightly", "devel", "test"))]
    return max(matching, key=lambda r: r.get("published_at") or "", default=None)


def same_tag(pinned, latest):
    return pinned.lstrip("vV").lower() == latest.lstrip("vV").lower()


def main():
    games = catalog_games()
    if not games:
        print("No GitHub-backed PC games found in rendered desktop entries.", file=sys.stderr)
        return 2
    counts = Counter()
    var_cache = {}
    token = github_token()
    print(f"GitHub PC game releases ({len(games)} catalog entries):")
    for stem, repo in games:
        try:
            pin = pinned_tag(stem, var_cache)
            release = latest_release(repo, stem, pin, token)
            if release is None:
                status, detail = "NO_RELEASE", repo
            else:
                tag = release["tag_name"]
                if pin is None:
                    status, detail = "REVIEW", f"{tag} (no release pin in group_vars)"
                elif same_tag(pin, tag):
                    status, detail = "CURRENT", tag
                else:
                    status, detail = "CANDIDATE", f"{pin} -> {tag}"
                detail += f"  {release.get('html_url') or 'https://github.com/' + repo + '/releases'}"
        except (HTTPError, URLError, TimeoutError, ValueError, KeyError) as exc:
            # Never format raw exceptions: urllib can include Authorization
            # header values in a malformed-header error.
            reason = f"HTTP {exc.code}" if isinstance(exc, HTTPError) else type(exc).__name__
            status, detail = "ERROR", f"{repo}: {reason}"
        counts[status] += 1
        print(f"  {status:10} {stem:30} {detail}", flush=True)
    print("  " + ", ".join(f"{key.lower()}={counts[key]}" for key in ("CURRENT", "CANDIDATE", "REVIEW", "NO_RELEASE", "ERROR")))
    return 1 if counts["CANDIDATE"] or counts["REVIEW"] or counts["ERROR"] else 0


if __name__ == "__main__":
    sys.exit(main())
