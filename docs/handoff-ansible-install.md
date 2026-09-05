# Handoff: kick off the Odin Ansible installation

## Objective

Provision the first, core-only emulator milestone on the `mateuspim` Omarchy
workstation. Keep the existing Steam installation native. Use a rootless Podman
Distrobox for ES-DE, RetroArch, Dolphin, DuckStation, PCSX2, PPSSPP, Flycast,
and melonDS.

Do not enable RPCS3, Eden, Cemu, xemu, shadPS4, Supermodel, Xenia, game-mod
roles, or firmware-specific roles during this handoff.

## Repository state

- Fork: <https://github.com/mateuspim/distrobox-gaming>
- Local checkout: `/home/pym/Projects/distrobox-gaming`
- Branch: `master`
- Tailored baseline commit: `57a6330` (`Add Omarchy Odin core profile`)
- Upstream remote: `https://github.com/akitaonrails/distrobox-gaming.git`
- Entry playbook: `ansible/site-core.yml`
- Machine profile: `ansible/profiles/odin.yml`
- Steam package and container launcher: disabled by `dg_install_steam: false`
- Advanced emulator packages/configs: disabled by
  `dg_advanced_emulators_enabled: false`

At handoff creation, the worktree was clean before this document update and the
tailored baseline was already pushed to `origin/master`.

## Observed host state

- Omarchy `4.0.2-1`, Arch Linux.
- User identity `1000:1000` (`pym`).
- AMD Ryzen 9 9900X, 60 GiB RAM.
- NVIDIA RTX 4080 plus AMD integrated graphics.
- NVIDIA kernel/userspace/lib32 packages all version `610.57.04`.
- Native Steam `1.0.0.87-3` installed.
- `xpadneo-dkms` and `steam-devices` installed.
- Sleipnir: Btrfs games disk at `/mnt/sleipnir`, approximately 1.9 TB free.
- `/etc/fstab` declares Sleipnir `rw`; the managed agent namespace reported it
  as `ro`. Validate from the user's normal terminal and stop if it is not
  writable.
- Docker is installed but the user is not in the `docker` group. Do not alter
  Docker group membership; this plan uses rootless Podman.
- `ansible-playbook`, `ansible-galaxy`, `distrobox`, and `podman` were missing.

## Guardrails

1. Use `omarchy pkg add` for host packages; never edit `/usr/share/omarchy`.
2. Run privileged package installation in an interactive terminal so `sudo`
   can request a password normally.
3. Do not download ROMs, console keys, BIOS files, firmware, or proprietary
   system modules.
4. Do not run upstream `ansible/site.yml`; it includes Akita's personalized
   and firmware-heavy setup.
5. Do not enable or install Steam in the container.
6. Do not use `sudo ansible-playbook`. Rootless Podman and the container must
   remain owned by user `pym`.
7. Stop at the first failed validation gate. Do not compensate with broad
   permissions, recursive ownership changes, or Docker group membership.

## Phase 0: preflight from the normal desktop terminal

```sh
cd /home/pym/Projects/distrobox-gaming
git status --short --branch
git pull --ff-only origin master
id
findmnt -no SOURCE,TARGET,FSTYPE,OPTIONS /mnt/sleipnir
nvidia-smi
vulkaninfo --summary
```

Expected:

- Git worktree clean and synchronized with `origin/master`.
- UID and GID are both `1000`.
- Sleipnir options include `rw`.
- `nvidia-smi` reports the RTX 4080 and driver `610.57.04`.
- Host Vulkan reports the NVIDIA GPU. The AMD iGPU may also be listed.

Confirm Sleipnir is genuinely writable with a narrowly scoped probe:

```sh
touch /mnt/sleipnir/.dg-write-test
rm /mnt/sleipnir/.dg-write-test
```

If either command fails, stop. Resolve the mount outside this playbook before
continuing.

## Phase 1: host prerequisites

Install only the required Arch repository packages:

```sh
omarchy pkg add ansible distrobox podman
```

Then validate rootless Podman as the normal user:

```sh
ansible-playbook --version
distrobox --version
podman version
podman info
podman ps
```

`podman info` must not report a rootful service requirement or permissions
error. Docker does not need to be running.

Install the repository's pinned Ansible collection:

```sh
cd /home/pym/Projects/distrobox-gaming
ansible-galaxy collection install -r ansible/collections/requirements.yml
```

## Phase 2: storage skeleton

Create only the empty directories expected by the committed Odin profile:

```sh
mkdir -p /mnt/sleipnir/Emulation/EmuDeck/Emulation/bios
mkdir -p /mnt/sleipnir/Emulation/EmuDeck/roms
mkdir -p /mnt/sleipnir/Emulation/EmuDeck/roms_mid
mkdir -p /mnt/sleipnir/Emulation/EmuDeck/roms_heavy
mkdir -p /mnt/sleipnir/Emulation/EmuDeck/roms_rare
mkdir -p /mnt/sleipnir/Emulation/ROMS_FINAL
```

Do not copy firmware or games yet. Confirm all new paths are owned by
`1000:1000` and writable without `sudo`:

```sh
find /mnt/sleipnir/Emulation -maxdepth 3 -type d -printf '%u:%g %m %p\n'
test -w /mnt/sleipnir/Emulation/EmuDeck/roms
```

## Phase 3: static validation

Run from `ansible/`:

```sh
cd /home/pym/Projects/distrobox-gaming/ansible
ansible-playbook --syntax-check site-core.yml -e @profiles/odin.yml
ansible-playbook site-core.yml -e @profiles/odin.yml --list-hosts
ansible-playbook site-core.yml -e @profiles/odin.yml --list-tags
```

Do not proceed if syntax checking reports undefined variables, missing roles,
inventory errors, or collection errors. Fix and commit repository issues first.

## Phase 4: staged provisioning

Run one stage at a time. Capture the output from every command before moving to
the next gate.

### 4.1 Host/path checks

```sh
ansible-playbook site-core.yml -e @profiles/odin.yml --tags check
```

Expected: identity, storage, and runtime checks pass. Warnings for optional BIOS
or advanced-console assets are acceptable; hard failures are not.

### 4.2 Create the container

```sh
ansible-playbook site-core.yml -e @profiles/odin.yml --tags create
distrobox list
podman ps -a
```

Expected: one rootless container named `gaming`, using
`docker.io/library/archlinux:latest`, with its custom home below
`/mnt/sleipnir/Emulation/distrobox/gaming`.

Before installing packages, validate NVIDIA visibility:

```sh
distrobox-enter -n gaming -- nvidia-smi
```

Stop if the RTX 4080 or matching driver is not visible.

### 4.3 Bootstrap core packages

```sh
ansible-playbook site-core.yml -e @profiles/odin.yml --tags bootstrap
```

This performs a container upgrade and installs Arch/AUR packages, so it may run
for a while. It must not install the container `steam` package, RPCS3, Eden,
Cemu, xemu, shadPS4, or Supermodel under the Odin profile.

Verify the intended package boundary:

```sh
distrobox-enter -n gaming -- sh -lc \
  'for cmd in es-de retroarch dolphin-emu duckstation-qt pcsx2-qt PPSSPPSDL flycast melonDS; do
     command -v "$cmd" || exit 1
   done'
distrobox-enter -n gaming -- sh -lc \
  'for p in steam rpcs3-bin eden-bin cemu-bin xemu-bin shadps4-bin supermodel; do pacman -Q "$p" 2>/dev/null && exit 1 || true; done'
distrobox-enter -n gaming -- vulkaninfo --summary
```

Expected: all core commands resolve, excluded packages remain absent, and
Vulkan reports the RTX 4080.

### 4.4 Render core configuration and launchers

```sh
ansible-playbook site-core.yml -e @profiles/odin.yml --tags configure
```

Expected:

- ES-DE configuration exists below the container home.
- Host desktop entries are installed under
  `~/.local/share/applications/` only for commands that actually exist.
- No `gaming-steam.desktop` is installed.
- No files under `/usr/share/omarchy` are changed.

## Phase 5: smoke tests

Start ES-DE from the Omarchy application launcher or run:

```sh
distrobox-enter -n gaming -- es-de
```

Validate in this order:

1. ES-DE opens without a black or transparent window.
2. Audio reaches the host PipeWire session.
3. `vulkaninfo --summary` inside the box continues to show the RTX 4080.
4. A connected controller is visible; do not apply Akita's 8BitDo profile to a
   different controller.
5. Test only a legally supplied homebrew or owned-game dump.
6. Test one RetroArch system before standalone emulators.
7. Test DuckStation, PCSX2, Dolphin, PPSSPP, Flycast, and melonDS separately as
   their required user-supplied assets become available.

## Phase 6: idempotence and commit

After the first successful configuration run:

```sh
ansible-playbook site-core.yml -e @profiles/odin.yml
```

Review the recap. A second run must not recreate the container or repeatedly
rewrite unchanged state. Investigate unexpected changes before enabling more
systems.

Commit only source configuration and documentation. Never add anything below
ROM, BIOS, firmware, save, cache, or runtime directories.

## Rollback and recovery

Before any rollback, collect state without deleting anything:

```sh
distrobox list
podman ps -a
podman inspect gaming
git status --short --branch
```

Do not remove the container automatically as part of this handoff. If creation
or bootstrap fails, retain it for diagnosis. Container deletion and storage
cleanup require an explicit user decision after logs have been reviewed.

## Completion criteria

The handoff is complete when:

- Rootless Podman and Distrobox work as user `pym`.
- The `gaming` container exists on Sleipnir.
- The RTX 4080 is visible through Vulkan inside the container.
- All eight core applications are installed and launchable.
- Native Steam remains untouched and no container Steam launcher exists.
- ES-DE opens from Omarchy.
- Audio and one controller pass smoke testing.
- A second Ansible run is acceptably idempotent.
