# X5-mini-camera_teardown_reverse
Technical information about the chinese X5 mini wifi camera obtained by inspecting and reversing its hardware and firmware

<img src="/images/camera_box.webp" height="200">

## Hardware

SoC: Augentix HC1703
...

## Software

Bootloader: U-Boot 2016.03 (Aug 17 2023 - 18:00:58 +0800)
...

## Firmware

The factory U-boot bootloader tries to read a firmware upgrade file named `xyx.upgrade.bin` and a `xyx.config` config file from the sd card to upgrade the firmware.

### Firmware upgrade file header

The firmware upgrade file must have a valid header in order to be accepted by the bootloader and be flashed.  
The header size is 64 bytes.  
This is the header layout:

![reversed_firmware_header.png](/images/reversed_firmware_header.png)

$\large{\color{olive}{\textsf{Magic}}}$: `27 05 19 56` (4 bytes).  
$\large{\color{RoyalPurple}{\textsf{Header Checksum}}}$: CRC32 of the header with this checksum itself (0x04 to 0x07) set to zeros (4 bytes).  
$\large{\color{teal}{\textsf{Version Time 1}}}$: Epoch timestamp, indicating the FW version time, used for example by the bootloader to check if the current version is up to date. It avoids to reflash the fw from sdcard on reboot after an upgrade (4 bytes).  
$\large{\color{BrickRed}{\textsf{Total Size}}}$: Total size in bytes the whole file without the header (from "#BOOT" to end) as hex value (4 byte).  
$\large{\color{Plum}{\textsf{Packet ID}}}$: ID used by the bootloader to compare fw versions when upgrading (in combination with FW version 1) (8 bytes).  
$\large{\color{green}{\textsf{Firmware Checksum}}}$: CRC32 of the whole file without the header (4 bytes).  
$\large{\color{blue}{\textsf{Version Time 2}}}$: Epoch timestamp probably used as secondary FW version time, couldn't figure out where it is used (4 bytes).  

### Firmware upgrade config

The "xyx.config" can be used to control the behavior of the bootloader during the upgrade.  
It can be used to skip the version control checks during an upgrade, by configuring it like this:
```
force_update=1

```

### Firmware layout

The firmware (without the header) is what gets written to the internal NOR flash.  
This is its layout (flash partitions):

```
0x000000000000-0x000000040000 : "boot"
0x000000040000-0x000000050000 : "bootenv"
0x000000050000-0x000000210000 : "linux"
0x000000210000-0x0000006d0000 : "rootfs"
0x0000006d0000-0x0000007d0000 : "usrdata"
0x0000007d0000-0x0000007e0000 : "config"
0x0000007e0000-0x0000007f0000 : "database"
0x0000007f0000-0x000000800000 : "factory"
```

The "bootenv" partition starts with a checksum.  
It is the CRC32 of the bootenv partition itself, without the checksum part (first 4 bytes), in reverse bytes order. 
