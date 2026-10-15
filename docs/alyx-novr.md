# Half-Life: Alyx NoVR

Optional overlay for Steam app 546560. The game must be installed in a mounted
Steam library visible inside the `gaming` distrobox. Set
`dg_alyx_novr_steam_library_root` in `ansible/host_vars/localhost.yml` to the
directory containing `steamapps/`, then run from `ansible/`:

```sh
ansible-playbook install-alyx-novr.yml
```

The role downloads the pinned upstream `steam_deck` branch snapshot into a
reusable cache, backs up the two original game files it replaces under
`game/.dg-hla-novr/original/`, and records every installed file in
`game/.dg-hla-novr/manifest.json`. It does not alter saves.

The [upstream Linux instructions](https://www.moddb.com/mods/half-life-alyx-novr/downloads/half-life-alyx-novr-steam-deckmanual-install-january-5th-2026)
require the **Windows game build via Proton**. In Steam, open Alyx's Properties,
force a Proton compatibility tool, allow Steam to finish changing depots, and
set launch options to:

```text
-novr -vsync +vr_enable_fake_vr 1
```

When Steam is closed, the playbook also pins Proton 11 and writes these launch
options. Steam rewrites its config while running, so in that case the playbook
leaves Steam's settings alone and they must be set in its UI. To remove the overlay:

```sh
ansible-playbook install-alyx-novr.yml -e dg_alyx_novr_revert=true
```

The remover refuses to overwrite files changed since installation. Switching
Steam back to the native Linux build is a separate Steam Properties action.
