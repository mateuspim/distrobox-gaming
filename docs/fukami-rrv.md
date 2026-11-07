# Ridge Racer V via Fukami

The optional `install_fukami` role installs [Fukami](https://github.com/danisandoval/fukami) v1.1.0 alongside PCSX2. Fukami is a static recompilation of Ridge Racer V (USA, SLUS-20002). The role uses the official Linux release and the owned `.cue`/`.bin` disc pair under `dg_rom_heavy_root`. It verifies that the cue refers to the configured bin; Fukami verifies the disc contents and extracts what it needs on first launch. The original disc files remain untouched.

From `ansible/`, run `ansible-playbook install-fukami.yml` or `ansible-playbook site.yml --tags fukami`. Override `dg_fukami_disc_cue` and `dg_fukami_disc_bin` in `host_vars/localhost.yml` if the game lives elsewhere. The launcher appears as **Ridge Racer V · Fukami**. Saves, settings and extracted game files live in Fukami's user data directory (`~/.local/share/Fukami`); retain that directory during upgrades.

The role applies a one-time baseline of 4K output, 6× internal resolution, 16× anisotropic filtering, bilinear 3D textures, longer scenery draw distance and high car detail. Fukami's game clock is capped around 60 fps, so unpaced mode stays off. Native SDL controller input is enabled in analog mode with rumble; the connected 8BitDo pad is recognized by SDL. The one-time marker preserves later changes made in Fukami's settings menu.

The v1.1.0 [Linux build](https://github.com/danisandoval/fukami/releases/tag/v1.1.0) targets SteamOS 3.7 or later. On this host, first launch verified and unpacked the USA disc and rendered the Namco intro. A player-driven race and controller input have not been checked. Press F1 or Esc for settings; the current release does not support in-game controller remapping.
