# Master System hacks and homebrew

Three separate `.sms` files were added to `dg_emudeck_root/roms/mastersystem/`
on 2026-10-17. The original ROMs were not changed. These are currently manual
library additions, not entries in the `install_rom_patches` Ansible role; a
fresh rebuild must repeat the steps below. The release ZIPs were fetched from
SMS Power for this install and temporary copies were removed afterward.

| Release | Input | Installed output (SHA-256) |
| --- | --- | --- |
| [Sonic the Hedgehog — Genesis Mod v1.05](https://www.smspower.org/Hacks/SonicTheHedgehog-SMS-Genesis-Mod), `SonicTheHedgehog-SMS-Genesis-Mod-1.05.zip` | `roms/mastersystem/Sonic The Hedgehog (USA, Europe, Brazil) (En).sms`, SHA-256 `6ad738965ece231427ee046b9905cfee470d5c01220afdd934da4673e4a2458b` | `Sonic The Hedgehog (Genesis Mod v1.05) (Hack).sms`, `2004129a204c882c1e638834e02b2bf52d4e115e6e01d34fe5869269a289448e` (262,144 bytes) |
| [Hang-On — Enhanced v1.1](https://www.smspower.org/Hacks/HangOn-SMS-Enhanced-Mod), `HangOn-SMS-Enhanced-Mod-1.1.zip` | `dg_roms_final_root/mastersystem/Hang On (Japan) (En).zip` → `hang-on (japan).bin`, SHA-256 `3de56be8f38d3bdf63efe08517336b67da090f9b640035f0c40b4b3fb9436812` | `Hang-On (Japan) (Enhanced v1.1) (Hack).sms`, `762c65094843ce08d6ded1c53ab901ab9618008ee19515bf533da4c8a51b3c7f` (32,768 bytes) |
| [Lunar Skirmish v64](https://www.smspower.org/Homebrew/LunarSkirmish-SMS), `LunarSkirmish-SMS-v64.zip` | Complete homebrew ROM, `lunar_skirmish_v64.sms` inside the ZIP; no base or patch | `Lunar Skirmish (v64) (Homebrew).sms`, `6180d7ea792c2be38fee1d3a31fb0d0d640f9ec2c60232cb603d7f24ed12c50a` (425,984 bytes) |

To rebuild, download those exact release ZIPs from the linked pages and extract
the Sonic IPS, Hang-On BPS, and Lunar `.sms` to a temporary directory. Verify
the input hashes above first. Apply Sonic's IPS and Hang-On's BPS to separate
outputs with `ansible/roles/install_rom_patches/files/apply_ips.py` and
`apply_bps.py`; both tools require the base and expected output SHA-1:

| ROM | Base SHA-1 | Output SHA-1 |
| --- | --- | --- |
| Sonic | `6b9677e4a9abb37765d6db4658f4324251807e07` | `e44d8e7c8ffeccfbb4f71d405334d209024b5661` |
| Hang-On | `43552f58f0c0c292f3e4c1b1525fd0344dc220c6` | `751760105e190103e03c8f9540bbe3935b8c40a9` |

Hang-On's BPS file also verifies its own patch, source, and target CRC32s. The
installed Hang-On output was independently checked against that BPS target
checksum after applying the ZIP's IPS variant. Copy the verified outputs and
the Lunar ROM under the installed names above. A file/hash check passed for
all three NAS copies; emulator launch and gameplay have not been tested.

For example, after extracting the two patches and the Japanese Hang-On ROM to
a scratch directory, run the hash-checking appliers from the repository root:

```sh
python3 ansible/roles/install_rom_patches/files/apply_ips.py \
  "<EmuDeck>/roms/mastersystem/Sonic The Hedgehog (USA, Europe, Brazil) (En).sms" \
  "<scratch>/Sonic Genesis for Master System v1.05.ips" \
  "<scratch>/Sonic The Hedgehog (Genesis Mod v1.05) (Hack).sms" \
  6b9677e4a9abb37765d6db4658f4324251807e07 \
  e44d8e7c8ffeccfbb4f71d405334d209024b5661
python3 ansible/roles/install_rom_patches/files/apply_bps.py \
  "<scratch>/hang-on (japan).bin" \
  "<scratch>/hangon-enhanced-1.1.bps" \
  "<scratch>/Hang-On (Japan) (Enhanced v1.1) (Hack).sms" \
  43552f58f0c0c292f3e4c1b1525fd0344dc220c6 \
  751760105e190103e03c8f9540bbe3935b8c40a9
```

These commands write only scratch outputs. Copy them to the EmuDeck
`roms/mastersystem/` directory after they verify; extract Lunar's
`lunar_skirmish_v64.sms` there under the installed name in the table. Remove
the scratch directory after comparing the final SHA-256 hashes.
