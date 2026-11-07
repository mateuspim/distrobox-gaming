# Midnight Club: Los Angeles — native Xbox 360 port (`install_midnightclub_la`)

[CrownParkComputing/Xbox360-Native-Ports](https://github.com/CrownParkComputing/Xbox360-Native-Ports/releases/tag/midnightclubla-v1)
ships a **native recompilation** of Midnight Club: Los Angeles — 30,205 PowerPC
functions rebuilt as native x86-64, with a native **Vulkan** renderer and native
audio (the "rex" / ReXGlue framework: `librexruntime.so` + `librexgpu-xenos.so`).
It runs on the RTX with **no emulator and no Xenia**.

The release is a **launcher + the title's checksums only — no game data**. You
supply your own **MC:LA Complete Edition (USA)** disc (title `545407F8`); the
role imports it into `assets/`.

## Install

```sh
cd ansible
ansible-playbook install-midnightclub-la.yml     # or: site.yml --tags midnightclub_la
scripts/install-host-launchers.sh                # refresh the host menu entry
```

Launcher `bin/midnightclubla`; host/Walker entry **"Midnight Club: Los Angeles"**;
`ogm` id `midnightclubla`. Revert with `-e dg_mcla_revert=true` (removes the
launcher + install dir; your ISO is untouched).

## How it works

- Downloads the pinned `midnightclubla-launcher-linux-x86_64.tar.zst`
  (sha256-pinned in `group_vars/all/midnightclub_la.yml`) and extracts it to
  `tools/midnightclubla/`.
- Runs the bundled `tools/import_content.sh <iso>` **headlessly**: the shipped
  `rexiso` reads the XDVDFS `.iso`, copies the disc tree into `assets/`, and
  verifies it against `content/content.sha256`. Your Complete Edition (USA) ISO
  matches the exact build, so no region warning. (import also accepts a
  `.rar/.zip/.7z` or an extracted folder, and STFS/XBLA packages.)
- Deploys `bin/midnightclubla`, which focuses DP-1, pins the **nvidia Vulkan
  ICD**, and runs the port's own `run.sh` (which sets `LD_LIBRARY_PATH` and execs
  the tuned binary). Per-title tuning lives in `midnightclubla.toml` (host
  render-target path, `clear_memory_page_state=false`, `gpu_hot_page_frames=3`,
  strict-FIFO present for the VRR panel, etc.).

## Rendering upgrades (2026-09-28)

The launcher appends two rex cvars (`dg_mcla_resolution_scale` /
`dg_mcla_aniso_override` in `group_vars/all/midnightclub_la.yml`):

- `--resolution_scale=3` — targets 3840x2160 internal rendering from the
  game's 1280x720 base. A launch log confirmed
  `src_scaled=3840x2160, active=3840x2160`; gameplay still needs a visual check
  for post-processing and HUD artifacts.
- `--anisotropic_override=5` — force 16x AF.

If a scene ever renders wrong (post-processing/HUD glitches are the usual
resolution-scale casualties), set `dg_mcla_resolution_scale: 1` and re-run the
playbook. The upstream rexmenu offers 30/60/120/240 FPS caps, but this installed
standalone `run.sh` starts the game directly, with no verified external FPS-cap
setting. Its `CONVERSION.md` reports around 11 FPS in free roam on an RTX 3060,
and this installation's tuning comments recorded about 20 FPS parked in free
roam. A 60 FPS cap or timing patch is not evidence that gameplay reaches 60 FPS.
The port uses strict FIFO presentation to avoid VRR flicker. Hyprland
fullscreens the window shortly after launch.

Saves + settings live in `tools/midnightclubla/midnightclubla/user-data/`.
Controls: gamepad works via SDL (8BitDo native); keyboard = Return/Start,
Space/A, WASD stick, E accelerate.

ROM/disc: the Complete Edition (USA, Europe) ISO in
`roms_heavy/xbox360/`. Override `dg_mcla_iso` if yours lives elsewhere.

## Updating

Point `dg_mcla_release_tag` / `dg_mcla_asset_name` / `dg_mcla_asset_sha256` at a
newer release and re-run; the extract is version-gated and the import is skipped
once `assets/default.xex` exists (delete `assets/` to re-import a different disc).
