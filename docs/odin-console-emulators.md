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

## Read-only SMB ROM library

The focused playbook can mount one SMB share on the **host** and bind only its
`switch`, `ps3`, `ps4`, and `wiiu` directories into the existing EmuDeck
paths. It never downloads, copies, extracts, or modifies games, keys, BIOS,
firmware, or PS4 system modules. Existing local directories are covered while
the bind mount is active; their contents are not deleted and return if the
mount is removed.

Keep the UNC address and credentials out of tracked profiles. Add the share
address to ignored `ansible/host_vars/localhost.yml` (SMB URIs use `//`, not
`smb://`):

```yaml
dg_smb_roms_enabled: true
dg_smb_rom_share: //server/roms
# These defaults are optional to repeat:
# dg_smb_rom_mountpoint: /mnt/roms
# dg_smb_rom_credentials_file: /etc/smbcredentials/distrobox-gaming-roms
```

Create the root-only credentials file on the host; do not put it in Ansible,
a shell history, or this repository:

```sh
sudo install -d -m 0700 /etc/smbcredentials
sudoedit /etc/smbcredentials/distrobox-gaming-roms
sudo chmod 0600 /etc/smbcredentials/distrobox-gaming-roms
```

Its contents use the standard `mount.cifs` format:

```ini
username=your-smb-user
password=your-smb-password
# domain=optional-domain
```

Then mount, map, configure, and verify only the selected console setup:

```sh
ansible-playbook site-console-emulators.yml -e @profiles/odin.yml \
  --tags configure,verify --ask-become-pass
```

The role writes a managed `/etc/fstab` root mount plus one read-only bind
mount per system in `dg_smb_rom_systems` (default: all four). If the share
lacks a system directory, leave it out, e.g.
`dg_smb_rom_systems: [switch, ps3, wiiu]` in `host_vars/localhost.yml`; that
system keeps its local EmuDeck directory. It may stop the existing `gaming` distrobox once if its private mount
namespace cannot see new host mounts; this preserves the container image layer
and the bind-mounted box home, but closes programs running in that box. A
rerun is idempotent and confirms host CIFS mounts, rootless-box read access,
the ES-DE paths and enumeration, the four package/launcher boundaries, and
desktop-file validity.

The expected share layout and mappings are:

| Share directory | Existing emulator / ES-DE path |
| --- | --- |
| `switch/` | `{{ dg_emudeck_root }}/roms_heavy/switch` (Eden) |
| `ps3/` | `{{ dg_emudeck_root }}/roms_heavy/ps3` (RPCS3) |
| `ps4/` | `{{ dg_emudeck_root }}/roms_rare/ps4` (shadPS4) |
| `wiiu/` | `{{ dg_emudeck_root }}/roms_heavy/wiiu` (Cemu) |

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
