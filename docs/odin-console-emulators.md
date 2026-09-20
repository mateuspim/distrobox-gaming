# Odin selected console emulators

The Odin profile keeps the historical broad advanced tier off and enables only
Eden, shadPS4, RPCS3, and Cemu. The focused playbook extends the already
working `gaming` distrobox without running `site.yml`, creating a second Steam
installation, or invoking any game- and mod-specific roles.

## Provision and validate

Run these commands from `ansible/` after reviewing the AUR recipes:

```sh
ansible-playbook --syntax-check site-console-emulators.yml -e @profiles/odin.yml
ansible-playbook site-console-emulators.yml -e @profiles/odin.yml --tags bootstrap
ansible-playbook site-console-emulators.yml -e @profiles/odin.yml --tags configure
```

The bootstrap stage selects only `eden-bin`, `shadps4-bin`, `rpcs3-bin`, and
`cemu-bin` in addition to the already installed core package set. It does not
select xemu, Supermodel, Vita3K, 3dsconv, extract-xiso, flips, container Steam,
or any optional-app package.

The configure stage adds ES-DE systems for Switch, PS3, PS4, and Wii U; adds
one host launcher for each emulator; and creates only the PS3 and Switch
maintenance scripts that match the selected emulators. Check the result with:

```sh
distrobox-enter -n gaming -- sh -lc '
  for cmd in eden shadps4 rpcs3 cemu; do command -v "$cmd" || exit 1; done
  vulkaninfo --summary
'
distrobox-enter -n gaming -- sh -lc '
  for p in xemu-bin supermodel vita3k-bin 3dsconv extract-xiso-bin flips steam; do
    pacman -Q "$p" >/dev/null 2>&1 && { echo "unexpected package: $p"; exit 1; }
  done
'
```

The host application directory should contain `gaming-eden.desktop`,
`gaming-shadps4-gui.desktop`, `gaming-rpcs3.desktop`, and
`gaming-cemu.desktop`, along with the existing core launchers. It should not
gain xemu, Supermodel, Vita3K, Eden Cheat Manager, or Steam launchers.

Rerun the same bootstrap and configure commands after the smoke checks. The
second runs should report no unexpected changes.

## User-supplied assets for game testing

Nothing in this playbook downloads or copies keys, firmware, BIOS files, game
dumps, or PS4 system modules.

| Emulator | Supply before testing an owned title |
| --- | --- |
| Eden | Your dumped Switch `prod.keys` and `title.keys`, required firmware when the title requires it, and an owned game dump. Import them through Eden. |
| RPCS3 | The official PS3 firmware PUP obtained by you, installed through RPCS3, plus an owned PS3 disc dump or legitimately installed package. |
| shadPS4 | A legally dumped, decrypted PS4 game directory. Individual titles may need their own compatibility settings or system material; this setup does not acquire or seed PS4 system modules. |
| Cemu | An owned Wii U dump (`.wua`, `.wud`, `.wux`, or the title's `.rpx`). A dumped MLC/system-data set is optional and only needed by titles or features that depend on it. |

The shadPS4 baseline deliberately skips the repository's Driveclub patches,
per-game profiles, addon directory, and QtLauncher-managed build. They become
available only if `dg_shadps4_seed_game_profiles_enabled: true` is deliberately
set in a local override; do that only for a machine using those tested game
profiles.
