# Omarchy/Odin profile

This fork keeps Steam native on Omarchy and uses the `gaming` distrobox for a
reproducible ES-DE and emulator stack. Machine-specific, non-secret settings
are committed in `ansible/profiles/odin.yml`.

## Scope

The first milestone installs ES-DE, RetroArch, Dolphin, DuckStation, PCSX2,
PPSSPP, Flycast, and melonDS. RPCS3, Eden, Cemu, xemu, shadPS4, Supermodel, and
firmware/game-specific roles remain disabled until the core stack passes GPU,
audio, controller, and launcher validation.

Steam remains the native Omarchy installation. The core playbook does not
create, mount, or change a Steam library and does not render a container Steam
launcher.

## Host prerequisites

Use rootless Podman as the Distrobox backend. The existing Docker daemon is not
required and the user does not need membership in the privileged `docker`
group.

Required host commands:

```sh
distrobox
podman
ansible-playbook
```

Install the Ansible collection used by the roles:

```sh
ansible-galaxy collection install -r ansible/collections/requirements.yml
```

## Storage

The profile expects the games disk at `/mnt/sleipnir` and stores all emulator
data below `/mnt/sleipnir/Emulation`. Before provisioning, confirm the mount is
writable in the normal user session and create the required roots:

```sh
mkdir -p /mnt/sleipnir/Emulation/EmuDeck/Emulation/bios
mkdir -p /mnt/sleipnir/Emulation/EmuDeck/{roms,roms_mid,roms_heavy,roms_rare}
```

ROMs, saves, firmware, keys, and BIOS files are never committed. Supply only
assets dumped from hardware or games you own.

## Validate and provision

Run from `ansible/`:

```sh
ansible-playbook --syntax-check site-core.yml -e @profiles/odin.yml
ansible-playbook site-core.yml -e @profiles/odin.yml
```

Provisioning is not considered complete until a second run is idempotent and
the container passes these checks:

1. `vulkaninfo --summary` sees the NVIDIA RTX 4080.
2. ES-DE opens through its host desktop entry.
3. PipeWire audio works from the container.
4. A connected controller is visible and mapped explicitly.
5. One legally supplied test title works in RetroArch and each installed
   standalone emulator family.

## Advanced tier

After the core milestone, set this in a private/local override or update the
committed profile deliberately:

```yaml
dg_advanced_emulators_enabled: true
```

Advanced emulators still require their own firmware, keys, BIOS, or system
files. Do not run upstream's full `site.yml` until those paths and desired
systems have been reviewed; it includes Akita's game- and mod-specific roles.
