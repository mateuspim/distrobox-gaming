# Beetle Adventure Racing! Recompiled — `install_bar_recomp`

[danielgomesvieira2000/beetle-adventure-racing-recomp](https://github.com/danielgomesvieira2000/beetle-adventure-racing-recomp)
is an **N64Recomp + N64ModernRuntime + RT64 static recomp** PC port of Beetle
Adventure Racing! (N64, USA) — continued from bryankruman's original
BeetleRecomp. Opt-in role; installed 2026-09-28 at `v0.4.2-alpha`.

## Windows build under Wine (like Wave Race, unlike Pilotwings/CBFD)

Upstream ships **Windows-x64 only** — the native Linux build compiles but
crashes during boot (upstream `docs/KNOWN_ISSUES.md`). So we run the prebuilt
Windows build under **Wine**, with RT64's D3D12 going through GE-Proton's
**vkd3d-proton** to the RTX — the same path as `install_waverace_recomp`
(DXVK/vkd3d DLLs staged into the prefix from GE-Proton, `WINEDLLOVERRIDES`
`dxgi,d3d11,d3d12,d3d12core=n,b`, VK_ICD pinned nvidia). Revisit for a native
Linux build once upstream's Linux boot crash is fixed.

Features at v0.4.2: RecompFrontend launcher/settings/binding UI, widescreen
with HUD expansion, 1x/2x/4x draw distance, internal-resolution scaling
(display-native default), MSAA + VI divot filter, high-FPS interpolation
(phase 1), Controller Pak saves, multiplayer.

## ROM (required)

**Beetle Adventure Racing! (USA) only** — z64 sha1
`e5ab4d226c08d22f68a2edcc48870203e67454b8` (16 MiB). The NAS dump
`ROMS_FINAL/n64/Beetle Adventure Racing! (USA) (En,Fr,De).v64` is
byte-swapped; the role converts it to big-endian `.z64` (kept next to the zip
on the NAS) and verifies the sha1.

## Install / run / revert

```sh
cd ansible
ansible-playbook install-beetle-recomp.yml     # or: site.yml --tags beetle_recomp
ansible-playbook install-beetle-recomp.yml -e dg_bar_revert=true
```

The launcher `bin/beetle-recomp` passes the verified `.z64` as argv (Wine `Z:`
path with forward slashes) — the frontend imports it as `bar.n64.us.z64` into
its data dir on first launch, so the ROM picker never blocks. Settings, saves
(`mempak_p0.pak`) and the cached ROM live in the prefix at
`drive_c/users/<user>/AppData/Local/beetle-adventure-racing-recomp/`.

Verified 2026-09-28 on the box: launcher menu rendered, 8BitDo auto-assigned
to Player 1, ROM imported, and the game booted into the car-select screen
(3D rendering through vkd3d-proton confirmed working). First launch lands on
the frontend menu — pick Start Game / press Enter.

One extraction quirk: the release zip uses **backslash** path separators, and
`unzip` on the NAS mount exits 1 on harmless attribute warnings — the role
accepts rc 0/1 and verifies the exe landed instead of trusting the exit code.
