# PS1 60 FPS patches on DuckStation

Most PS1-era racing games ran rendering at 30 FPS while physics/timers ran
at the 60 Hz NTSC vsync. Patches that double rendering to 60 FPS are
therefore usually safe — they don't desync the sim, just draw a frame for
every vsync instead of every other one.

## Colin McRae Rally 1 (SLUS-00431, USA)

**Fastest fix:** built-in developer cheat. Enter **`SILKYSMOOTH`** as the
driver name on a new profile. Game runs at 60 FPS natively. Draw distance
shortens slightly (roadside trees thin out) — cosmetic only, no physics
impact. First-party option, fully safe for daily play and speedruns.

No emulator-side configuration needed; works on any DuckStation version.

## Colin McRae Rally 2.0 (SLUS-01222, USA)

**No 60 FPS option exists on PS1.** The game is natively 30 FPS-locked
and no community GameShark / Action Replay / DuckStation hack unlocks it.
Verified against GameHacking.org and multiple mirrors — the only codes
published for SLUS-01222 are gameplay cheats (unlock cars/tracks, max
points, infinite repair). Nothing touches framerate.

The `SILKYSMOOTH` passphrase is **CMR1-only** (SLUS-00934); CMR2 has a
different driver-name cheat list (ALLTHEBUTTONS, GREATNEWS, etc.) with
no framerate entry.

The [CMR 2.1 fan romhack](https://www.romhacking.net/hacks/322/) is
**not a 60 FPS patch** — it fixes windscreen transparency + analog
input response only.

If you need 60 FPS CMR2, the PC version + `SilentPatchCMR2` mod is the
only option (out of scope for this repo — not an emulation target).

## Why these are safe

Colin McRae Rally 1 and 2 were built on PlayStation SDK's standard
vsync-interrupt timing — game logic ticks on the 60 Hz IRQ from the GPU,
then renders every *other* tick to keep within the console's fillrate
budget. Doubling the render rate (either via `SILKYSMOOTH` or a GameShark
address patch) just removes the "skip every other vsync" gate. Physics
step count per second is unchanged.

Contrast with games that tie physics directly to frame count (e.g.
Gran Turismo series, Ridge Racer V on PS2): doubling render there
doubles physics too, which desyncs replays, AI, and save compatibility.

## Gran Turismo 1 (SCUS-94194, USA Rev 1) & Gran Turismo 2 (SCUS-94455/94488, USA v1.2)

**Silent's 60 FPS patches** (original codes by asasega, expanded by
Silent/CookiePLMonster to re-enable the tire smoke + rear-view mirror
that GT1's leftover Hi-Fi mode disables) — deployed and on by default
since 2026-10-01 via `dg_duckstation_cheats`
(`cheats/SCUS-94194_60fps.cht`, `cheats/SCUS-944{55,88}_silent.cht`).
Version matters: GT1 uses the **NTSC-U 1.1** codes for our Rev 1 disc
(the CHTDB pack's same-named entry carries v1.0 addresses — wrong for
this disc); GT2 uses the **NTSC-U 1.2** codes.

Caveat per Silent: unlike CMR1, GT ties physics to render rate — at
60 FPS, **existing replays and rally-mode AI ghosts desync/break**.
Normal racing, licenses and time trials are unaffected. Toggle the
`60 FPS` cheat off in Game Properties → Cheats before watching replays
or racing rally events with ghosts.

Setup details + the libretro-cht activation trap:
[gt2-duckstation.md](gt2-duckstation.md).

## References

- [SILKYSMOOTH cheat description (SuperCheats)](https://www.supercheats.com/playstation/colin-mcrae-rally/649/silkysmooth-60-fps-br-open/)
- [Speedrun.com CMR1 cheat codes guide](https://www.speedrun.com/cmr1/guides/tvw00)
- [Speedrun.com CMR2 DuckStation settings](https://www.speedrun.com/cmr2/forums/13zdt)
- [GameHacking.org CMR2 NTSC-U codes](https://gamehacking.org/game/88607)
- [romhacking.net CMR 2.1 fan hack](https://www.romhacking.net/hacks/322/)
- [Silent's Blog — GT2 mods index](https://silentsblog.com/mods/gran-turismo-2/)
- [Console-Cheat-Codes — GT1 60 FPS](https://github.com/CookiePLMonster/Console-Cheat-Codes/tree/master/PS1/Gran%20Turismo/60%20FPS)
- [Console-Cheat-Codes — GT2 60 FPS](https://github.com/CookiePLMonster/Console-Cheat-Codes/tree/master/PS1/Gran%20Turismo%202/60%20FPS)
