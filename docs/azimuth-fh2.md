# Forza Horizon 2 via Azimuth

The optional `install_azimuth` role installs [Azimuth](https://almost-there-games.itch.io/azimuth) v0.9.8 through Proton for the Xbox One Forza Horizon 2 release v1.0.0.64. Azimuth is an experimental Windows wrapper; its author reports Linux support through Proton. The role validates `era.vbi`, `Mount/AppxManifest.xml`, `Mount/`, and `EmbeddedXvd/` before installing the wrapper. It does not modify the game files.

Place the verified `azimuth-windows-0.9.8.zip` under `dg_roms_final_root/PC/`, with its SHA-256 matching `group_vars/all/azimuth.yml`, and unpack the Xbox One game under `dg_azimuth_game_dir`. From `ansible/`, run `ansible-playbook install-azimuth.yml` or `ansible-playbook site.yml --tags azimuth`. Override `dg_azimuth_game_dir` and `dg_azimuth_proton` in `host_vars/localhost.yml` if needed. The launcher keeps its Proton prefix beside the wrapper in `dg_azimuth_compatdata` and uses the NVIDIA Vulkan driver. On first launch, select `dg_azimuth_game_dir` in Azimuth's folder picker if it is not already configured.

The installer is idempotent and keeps the source ZIP for reproducibility. Save data and game files must be preserved when updating or removing Azimuth.
