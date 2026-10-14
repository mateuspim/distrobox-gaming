# OpenSC2K

OpenSC2K is a native Linux remake of SimCity 2000. The optional
`install-opensc2k.yml` playbook installs the pinned upstream Linux x64 release
inside the `gaming` distrobox and adds an OpenSC2K host launcher. It does not
change the default rebuild path.

```sh
cd ansible
ansible-playbook install-opensc2k.yml
```

The playbook extracts the SimCity 2000 Special Edition for Windows 95 installer
from `dg_opensc2k_original_archive`, then extracts its game data without running
the Windows installer. OpenSC2K validates the extracted installation and imports
its graphics, audio, data, cities, and scenarios into its user data folder. The
playbook configures those packs for the games-menu launcher. The source archive
and executable hashes are pinned in `group_vars/all/opensc2k.yml`; override
the archive path in `host_vars/localhost.yml` if needed. Other editions may not
be accepted by OpenSC2K. The Linux release includes Godot and a SoundFont.

The program and extracted original files live under
`dg_box_home/tools/opensc2k`; imported packs, saves, and settings stay in
OpenSC2K's Godot user data directory. To remove the program and launcher while
keeping user data, run:

```sh
cd ansible
ansible-playbook install-opensc2k.yml -e dg_opensc2k_revert=true
```

See [upstream installation instructions](https://github.com/nicholas-ochoa/OpenSC2K/blob/main/docs/install.md)
for the supported import source and save format notes.
