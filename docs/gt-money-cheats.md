# Gran Turismo money cheats (all installed titles)

Money cheats for every Gran Turismo in the library, deployed Ansible-managed
and **on by default** (user request, 2026-09-29). All of them are
continuous/pinned writes: credits stay at the cap, purchases never drain.

| Game | Platform | Mechanism | Amount |
|---|---|---|---|
| GT1 (SCUS-94194, v1.1 Greatest Hits) | DuckStation | native `.cht` + game-ini enable | 1,000,000,000 Cr |
| GT2 Simulation v1.2 (SCUS-94488) | DuckStation | native `.cht` + game-ini enable | pinned at 354,615,039 Cr |
| GT3 A-spec (PBPX-95503/8AA991B0) | PCSX2 | NAS pnach cheat + `[Cheats] Enable` | pinned at ~1e12 Cr |
| GT4 Spec II (SCUS-97436/4CE521F2) | PCSX2 | repo pnach `SCUS-97436_4CE521F2-money.pnach` + `[Cheats] Enable` | pinned at 99,999,999 Cr |
| GT5 (BCUS98114, 2.11 + Master Mod) | RPCS3 | one-shot save edit (see below) | cash + cash_limit set to 99,999,999 |
| GT6 (BCUS98296) | RPCS3 | nothing applied — no save exists yet | — |

## DuckStation (GT1, GT2)

Two-part mechanism, both in `dg_duckstation_cheats` (emulators.yml) and
`seed_configs/tasks/duckstation.yml`:

1. `content` + `tag` deploys a DuckStation-native-format cheat file to
   `cheats/<serial>_<tag>.cht` (the loader glob-matches `<serial>*.cht`).
2. `enable_names` writes `[Cheats] EnableCheats = true` plus repeated
   `Enable = <name>` lines into `gamesettings/<serial>.ini`. On current
   DuckStation this game-ini string list is the ONLY thing that activates
   cheats at boot (`ReloadEnabledLists` in src/core/cheats.cpp).

Gotchas discovered while wiring this up:

- **GT2 disc set is anchored on SCUS-94455.** The log shows `Loading game
  settings from 'SCUS-94455.ini'` even when booting the Simulation disc
  (SCUS-94488), so the `[Cheats]` enable list must live in the 94455 ini.
  The money .cht is shipped under both serials.
- **GT1 revision matters.** Our CHD is redump Rev 1 / Greatest Hits (v1.1):
  EXE date 1998-06-17 read from the ISO9660 tree (v1.0 = 1998-04-15). The
  v1.0 money code (0x09B864) does not apply; we use the v1.1 address
  0x09B8F4 (`9009B8F4 3B9ACA00`).
- GT2's code is **v1.2-specific** (801D156A 1525 / 801D1568 E0FF). The
  commonly copied "Max Cash After One Race" codes are v1.0 and do nothing
  on our disc.

## PCSX2 (GT3, GT4 Spec II)

Mechanism (pcsx2.yml + pcsx2_textures role):

- `dg_pcsx2_cheat_files` deploys repo-local pnach files into `cheats/`.
- `dg_pcsx2_cheat_enables` writes repeated `Enable = <exact header>` lines
  under `[Cheats]` in `gamesettings/<SERIAL>_<CRC>.ini`; per-game
  `[EmuCore] EnableCheats = true` rides along in `dg_pcsx2_per_game_settings`.
- Bracketed cheats are OFF unless named in that list; unbracketed pnach
  lines always apply when cheats are enabled (the GT3 NAS pnach has none).

Game specifics:

- **GT3**: our "USA (v1.10)" ISO actually boots as the **PS2 Bundle** serial
  PBPX-95503, CRC 8AA991B0 (verified via emulog — plain crc32 of the ISO is
  NOT the PCSX2 CRC). Its symlinked NAS pnach already contained
  `[Simulation Mode Codes\Max Money]`; we just enable it. The retail
  SCUS-97102/85AE91B3 ini gets `Max Money` enabled too, in case the dump
  is ever swapped.
- **GT4**: the ISO is the **Spec II mod** (CRC 4CE521F2), so vanilla money
  codes don't apply — GT4 XOR-obfuscates credits with key
  `0x7A726F706C6C525E`, and under Spec II the variable sits at **0x9C86A8**
  (vanilla: 0xA1FCA8; address per ike9000's Spec II credits research,
  github.com/ike9000e/game-patches-or-codes). The old "ported experiment"
  cheats were removed: they used the vanilla address AND misunderstood the
  XOR encoding (the madcatz variant writes >4 quadrillion credits and
  glitches saves). Our file writes the correct XOR pair for the
  99,999,999 display cap. Re-verify the address if Spec II is ever updated
  to a build with a different CRC.
- Caveat: GT4 saves can corrupt if PCSX2's EE/FPU clamping is changed from
  defaults — leave clamping alone for GT4.

## RPCS3 (GT5, GT6)

No cheat-code path exists for PS3; it's save editing.

- **GT5**: RPCS3 stores saves **decrypted** and writes **no PARAM.PFD**, so
  upstream zyzalfors/GT5SaveEditor (which insists on PFD decryption) can't
  be used as-is. We rebuilt its GT5Save class as a small CLI wrapper
  (dotnet, in-box) that edits the plaintext `GT5.0` directly. Archived at
  `{{ dg_external_games_root }}/tools/gt5-save-editor/` (source + prebuilt
  `bin/`), deployed to the box at `~/.local/share/gt5-save-editor/` by the
  `install_gt5_master_mod` role (`--tags tools`).
  Usage: `gt5tool <path-to-GT5.0> read | set cash 99999999`.
  Already applied 2026-09-29: `cash` and `cash_limit` set to 99,999,999
  (backup of GT5.0 + PARAM.SFO at `~/.local/share/dg-backups/gt5-20260929/`).
  Note the save carries its own `cash_limit` field (was 2,000,000) — the
  Master Mod's raised money cap did not retro-apply to this existing save,
  so we raised it in the save itself.
  The Master Mod also gives free cars (START in Used Car Dealer, TRIANGLE
  on a color in New Dealer) and debug tickets (hold R1) — no save edit
  needed for those.
- **GT6**: no savedata exists yet (game never played far enough to save),
  so there was nothing to bump. When a save exists, use GTSaveData 2.3.0
  (linux-amd64, archived at `Emulators/tools/gtsavedata/`) or Razerman's
  GT6 Save Editor (Windows GUI, handles RPCS3 encrypted saves natively).
  Caveat: editors target 1.22-era saves while we pin GT6 at 1.05 for RPCS3
  stability — back up before the first edit.

## Sources

- [gamehacking.org GT1](https://gamehacking.org/game/88919) /
  [GT2 v1.2](https://gamehacking.org/game/88923) ·
  [Almar's Guides GT1 v1.1](https://almarsguides.com/retro/walkthroughs/PS1/Games/GranTurismo/Gameshark/Version1.1/) /
  [GT2 v1.2](https://almarsguides.com/retro/walkthroughs/PS1/Games/GranTurismo2/Gameshark/Version1.2/)
- [ike9000e/game-patches-or-codes](https://github.com/ike9000e/game-patches-or-codes) — GT4 Spec II credits address + XOR key
- [zyzalfors/GT5SaveEditor](https://github.com/zyzalfors/GT5SaveEditor) — GT5 save structure + crypto (we use the save layer only)
- [Razer2015/GTSaveData](https://github.com/Razer2015/GTSaveData) — GT5/GT6 save decrypt/encrypt (archived for GT6)
- [DuckStation cheats.cpp](https://github.com/stenzek/duckstation/blob/master/src/core/cheats.cpp) — game-ini enable mechanics
- [PCSX2 Patch.cpp](https://github.com/PCSX2/pcsx2/blob/master/pcsx2/Patch.cpp) — pnach enable mechanics
