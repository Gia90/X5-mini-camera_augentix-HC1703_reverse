# X5-mini-camera_teardown_reverse
Technical information about the chinese X5 mini wifi camera obtained by inspecting and reversing its hardware and firmware

![camera_box](/images/camera_box.webp)

## Hardware
SoC: Augentix HC1703


## Firmware
Bootloader: U-Boot 2016.03 (Aug 17 2023 - 18:00:58 +0800)


## OTA Firmware

The u-boot bootloader checks for a valid header in order to proceed with updating the firmware.
This is the revered layout of the OTA firmware header:

![reversed_firmware_header.png](/images/reversed_firmware_header.png)


