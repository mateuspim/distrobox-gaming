# Gran Turismo 1 & 2 on DuckStation

User complaint: DuckStation's default **Bilinear** texture filter
washes out GT2's hand-painted car and track art. Fix + best settings
for both GT1 (SCUS-94194) and GT2 (SCUS-94488 Simulation, SCUS-94455
Arcade — serials per redump; this doc had them swapped before
2026-09-28).

> **Why GUI changes "don't stick" for GT2:** DuckStation loads
> `gamesettings/<SERIAL>.ini` ON TOP of the global `settings.ini` —
> GT2 has a per-game profile, so the global texture filter you set in
> the GUI is ignored while GT2 runs. And both files are Ansible-seeded
> (`seed_configs`), so hand edits revert on the next playbook run.
> Change `dg_duckstation_settings` / `dg_duckstation_per_game_settings`
> in `ansible/group_vars/all/emulators.yml` and re-run
> `ansible-playbook site.yml --tags configs` instead.

## Global DuckStation defaults (benefit every PS1 game)

Written by `seed_configs` → `duckstation.yml` → `dg_duckstation_settings`:

| Section | Key | Value | Why |
|---|---|---|---|
| GPU | `Renderer` | `Vulkan` | NVIDIA ICD injected by launcher |
| GPU | `ResolutionScale` | `9` | 240p × 9 = 2160 — exactly the 4K panel's height, so the final display scale is 1:1 vertically |
| GPU | `TextureFilter` / `SpriteTextureFilter` | `Nearest` | User preference (2026-09-28): retro-crisp pixels, no smoothing at all |
| GPU | `Multisamples` | `4` | 4x MSAA, free on the RTX 5090 |
| Display | `Scaling` | `BilinearSharp` | Sharp-bilinear final upscale — crisp on non-integer (widescreen) stretches, no BilinearSmooth haze |
| GPU | `TrueColor` | `true` | 24-bit output, kills banding |
| GPU | `ScaledDithering` | `true` | Keep dither ON with TrueColor — Project Cerbera 2025 recalibration |
| GPU | `DisableInterlacing` | `true` | Progressive output |
| GPU | `PGXPEnable` / `Culling` / `TextureCorrection` | `true` | Stop texture swimming + geometry wobble |
| GPU | `PGXPDepthBuffer` / `PreserveProjFP` | `true` (global) | Helps most games; GT-family overrides to false (breaks GT skies) |
| CDROM | `LoadImageToRAM` | `true` | Load whole disc image (up to ~700 MB) into RAM on boot. Menu / track transitions become instant, especially on NFS-mounted ROMs |
| CDROM | `ReadSpeedup` / `SeekSpeedup` | `4` | Skip the emulated PS1 CD read/seek delays |
| MemoryCards | `Card1Type` | `PerGameTitle` | Separate virtual memcard per title — GT1 and GT2 saves don't collide |
| TextureReplacements | `EnableTextureReplacements` / `PreloadTextures` | `true` | Ready for drop-in retexture packs when they ship |
| Hacks | `MaxVRAMWriteSplits` | `1024` | Required by the Gran Turismo family per DuckStation wiki |

## Per-game overrides

Deployed via `dg_duckstation_per_game_settings` to
`~/.config/duckstation/gamesettings/<SERIAL>.ini`. Override the global
template when a title-specific tradeoff is needed.

### GT2 (SCUS-94488 Simulation, SCUS-94455 Arcade)

| Key | Override | Why |
|---|---|---|
| `TextureFilter` / `SpriteTextureFilter` | `Nearest` | Core user preference — pixel-crisp textures, zero blur |
| `PGXPDepthBuffer` / `PreserveProjFP` | **`false`** | Global true breaks GT2's skybox + distant road |
| `WidescreenHack` | **`false`** | DuckStation's built-in hack stretches HUD. Silent's 16:9 Widescreen 2.0 cheat (deployed + enabled by Ansible, see below) patches the viewport without breaking HUD |
| `Multisamples` | `8` | 8x MSAA, free on the RTX 5090 |
| `PerSampleShading` | `true` | Cleaner AA on alpha-tested textures (fences, trees) |
| `Console.EnableRAM8MB` | `true` | Pair with Silent's "Use 8 MB RAM for polygon buffers" cheat for full-LOD AI cars with no pop-in |
| `Display.AspectRatio` | `16:9` | Output aspect (not the broken hack). Use in tandem with Silent's widescreen cheat |

**Silent's GT2 cheat pack is deployed and on by default** (2026-10-01,
`dg_duckstation_cheats` → `cheats/SCUS-944{55,88}_silent.cht`, codes
verbatim from [Console-Cheat-Codes](https://github.com/CookiePLMonster/Console-Cheat-Codes/tree/master/PS1/Gran%20Turismo%202),
NTSC-U 1.2 files): **16:9 Widescreen**, **60 FPS** (Silent's improved
version — re-enables tire smoke + rear-view mirror), **Use 8MB RAM for
polygon buffers**, **Full detail AI cars**, **Slightly higher draw
distance**. Verified via boot log (`Enabled code from Cheats: ...` ×6
incl. money). 60 FPS caveat per Silent: existing replays and rally-mode
AI ghosts break — toggle `60 FPS` off in Game Properties → Cheats for
those events.

> **Activation trap (fixed 2026-10-01):** current DuckStation's boot-time
> parser (`ParseFile` in `src/core/cheats.cpp`) only understands the
> native `[Name]`-section .cht format. The libretro-format
> `cheatN_desc`/`cheatN_enable` pack this repo used to deploy as
> `<SERIAL>.cht` was never parsed at boot ("Unknown parameter" warnings,
> zero codes loaded) — so the widescreen set was silently INACTIVE
> despite the 2026-09-28 "verified" claim below, and GT2 ran stretched
> 4:3. Same for the GUI-added `[Patches] Enable` list in
> `SCUS-94455.ini` (60 FPS / Metric units / Widescreen 16:9 / 8MB RAM):
> `patches.zip` is not bundled with the Arch package, so no game patches
> ever load — that dead section was removed. The only live activation
> mechanism is the per-game ini `[Cheats] Enable = <exact name>` list,
> which the `silent` pack above uses.

Verified 2026-10-01 that this chain produces **true widescreen, not a
stretch**: the widescreen cheat now actually loads (see boot-log note
above), wheels measured circular in side-on 3D views and HUD sits
correctly at the frame edges. If the cheats ever fail to load (e.g.
renamed .cht), the same settings would silently fall back to a
stretched 4:3 frame — the tell is fat cars and an oval speedometer.

### GT1 (SCUS-94194)

Same template minus the GT2-specific 8 MB RAM hack. PGXP tradeoffs
identical. Widescreen uses DuckStation's built-in `WidescreenHack` (no
community cheat exists for GT1) — it patches the projection matrix, so
geometry is true 16:9; HUD may alias slightly.

**60 FPS (2026-10-01):** Silent's GT1 patch (asasega's original +
Silent's tire-smoke/rear-view-mirror re-enables) is deployed as
`cheats/SCUS-94194_60fps.cht` and enabled by default. Our disc is
Rev 1 / Greatest Hits (v1.1), so the **NTSC-U 1.1** codes are used
(`A60B6348`…) — the CHTDB pack's built-in "60 FPS" entry carries v1.0
addresses (`A60B6318`…) that do not apply; ours is named
`60 FPS (Silent)` so the two never collide.

### Money cheats

Both GT1 and GT2 boot with a pinned max-credits cheat (on by default,
Ansible-managed). Mechanism + the GT2 disc-set-ini gotcha and GT1 v1.1
revision note: [gt-money-cheats.md](gt-money-cheats.md).

> Bug fixed 2026-09-28: the seed used to write this profile as
> `SCUS-94949.ini` — a serial that does not exist — so GT1 silently ran
> on global defaults until then. Serial verified against the disc itself
> and the gamedb.

## Collection audit (2026-09-28)

Every other game in `roms/psx` was cross-checked against DuckStation's
built-in game database (`gamedb.yaml`): all rated **NoIssues**, and the
gamedb's per-title compat settings (CD speedup caps for Mega Man X4-X6/8,
MGS, Einhander, SOTN, Brave Fencer; display offsets for GT2/MGS/R4/CMR2;
`gpuPGXPTolerance=3` for Tekken 3; `gpuPGXPPreserveProjFP` for Ghost in
the Shell; `gpuLineDetectMode` for Soul Blade) are **auto-applied** — and
they win over our global seeds (`system.cpp` `LoadSettings()` applies
gamedb AFTER user settings; only per-game `gamesettings/*.ini` and cheat
overrides rank higher). So no additional per-game overrides are needed
beyond GT1/GT2. CMR2 (`SLUS-01222.ini`) is a user-made GUI profile
(cheats + 4:3 native), left as-is.

## Known mods / cheats worth knowing about (2026)

From **CookiePLMonster / Console-Cheat-Codes** (still active repo):

- **16:9 Widescreen 2.0** — viewport patch, 21:9 variant included. ✅ deployed + on by default (16:9)
- **60 FPS hack** — restores tire smoke + rear-view. ✅ deployed + on by default (GT1 and GT2)
- **Use 8 MB RAM for polygon buffers** + **Full detail AI cars** —
  pair with `EnableRAM8MB = true`. ✅ deployed + on by default
- **Slightly higher draw distance** — replay draw distance in races. ✅ deployed + on by default
- **Fixed Event Generator** — fixes arcade missing tracks. Not enabled (gameplay-affecting)
- **True Endurance**, **Metric Units**, **HUD toggle**, **Replay
  cameras in race**, **BGM switch** — not enabled; opt-in via Game
  Properties → Cheats (or add to `enable_names` in
  `dg_duckstation_cheats` to make permanent)

All ship as **DuckStation cheat codes** — no ISO patching, no
serial/CRC change. To add one permanently: drop a native-format
(`[Name]`-section) block into a `tag`+`content` entry in
`dg_duckstation_cheats` and list the name under `enable_names`, then
`ansible-playbook site.yml --tags configs`. Do NOT rely on the
libretro-format packs or the GUI's [Patches] list — see the activation
trap note above.

**GT2 Combined Disc** (https://github.com/CookiePLMonster/GT2-Combined-Disc)
— merges Arcade + Simulation into one disc. Repacks the ISO (new
CRC), but DuckStation still matches by disc serial so per-game
settings above still apply. Not deployed by this repo — it's
optional.

## Retextures — state of the art April 2026

**No consolidated retexture pack** has shipped for GT2. DuckStation
supports the drop-in system (`textures/SCUS-94488/` with hash-named
PNGs; `EnableTextureReplacements` already on globally so you're
ready), but no community pack is published as of April 2026 — only
WIP on [RetroGameTalk Personal Remasters thread](https://retrogametalk.com/threads/my-texture-pack-projects-personal-remasters-for-duckstation-pcsx2.15996/)
and YouTube demos.

For GT3 (different game): the ["Finished" pack on GBAtemp](https://gbatemp.net/threads/gran-turismo-3-scus-97102-texture-pack-finished.633662/).

If you want to dump-and-replace yourself, flip DuckStation's
**Advanced → Dump Replaceable Textures** and play through — PNG
dumps go to `textures/SCUS-94488/dumps/` (Simulation disc). Rename/edit/move to
`replacements/` to apply.

## ISO notes

Current setup points at the `GT2 (Simulation Mode) v1.2 patched` +
`GT2 Arcade` m3u under `EmuDeck/roms/psx/Gran Turismo 2/`. GT1 USA
Rev 1 was copied from `ROMS_FINAL/psx/` into the same roms/psx dir
for DuckStation to discover.

## References

- [Project Cerbera — DuckStation for GT2 (updated 2025-11-07)](https://projectcerbera.com/gt/2/duckstation/)
- [Silent's Blog — GT2 mods index](https://silentsblog.com/mods/gran-turismo-2/)
- [CookiePLMonster Console-Cheat-Codes](https://github.com/CookiePLMonster/Console-Cheat-Codes/tree/master/PS1/Gran%20Turismo%202)
- [WornOutWill — Best DuckStation Settings for PS1 Emulation (2026-03-13)](https://www.wornoutwill.com/2026/03/the-best-duckstation-settings-for-ps1.html)
- [PulseGeek — DuckStation Texture Filtering and Upscaling (2026-03-05)](https://pulsegeek.com/articles/best-duckstation-texture-filtering-and-upscaling/)
- [Nenkai GT Modding Hub — PS1/GT2 tooling](https://nenkai.github.io/gt-modding-hub/ps1/gt2/tools/)
- [DuckStation Wiki — Texture Replacement](https://github.com/stenzek/duckstation/wiki/Texture-Replacement)
