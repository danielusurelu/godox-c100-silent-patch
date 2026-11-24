# Unofficial GODOX C100 silent-shutter patcher (V1.1.6)

An **unofficial, local patcher** for the GODOX C100 V1.1.6 firmware that silences the
photo shutter. This repository does **not** include or distribute GODOX firmware: you
must obtain the official firmware from GODOX, keep it locally, and run the patcher on
your own copy.

> **Legal and safety notice**
>
> - This is an unofficial project. It is not affiliated with, authorized by, sponsored
>   by, or endorsed by GODOX.
> - This repository does not include or distribute GODOX firmware.
> - Download the official firmware directly from GODOX and supply it locally to the
>   patch script. The script modifies a local copy of the user-supplied official
>   firmware.
> - Flashing modified firmware can damage the camera and may void the warranty.
> - The project is provided without warranty.
> - Removing audible feedback means the camera may operate silently. Follow applicable
>   laws and obtain consent before photographing or recording people.

## What it does

The stock firmware plays `CAMERA.WAV` on every photo. The patch keeps the WAV header and
zeroes only the PCM samples, so the camera still thinks the sound exists but plays
nothing.

It does **not** remove the menu beep, power-on sound, or any other camera sound. It does
not change the camera code, the file size, the resource table, the bootloader, or the
application.

## Requirements

- Python 3.8+
- The stock GODOX C100 **V1.1.6** image:
  - size `0x1C1800` (1,841,152 bytes)
  - SHA-256 `411a553fc58810a1ea5b04ef46819deea317d574246ef5870c31d79d68f95036`

The patcher verifies the size and hash and refuses other images unless `--force` is
passed. It is tested only against this V1.1.6 image; other versions may use different
offsets.

## Apply the patch

```sh
python3 silence_camera.py GP_CARDVR_UPGRADE.BIN -o GP_CARDVR_UPGRADE_silent.bin
```

The script:

- verifies the stock size and SHA-256;
- creates a backup (`<input>.bak`) before writing;
- writes the patched image to a **new** output path and refuses to overwrite the input;
- refuses an existing output unless `--force` is passed.

Expected output SHA-256:
`592f5a97eaa7ef276cc914c12b2fe14188d208ab8e8faa98b084389cd9330b87`

The output keeps the exact same size, so the camera's updater and the resource table
still work.

## Flash

1. Rename the output to `GP_CARDVR_UPGRADE.BIN`.
2. Copy it to the **root** of a FAT32 or exFAT SD card.
3. With the camera off, insert the card and power on.
4. The LED flashes while the image is written (~10 s), then the camera powers off.
5. Power on again. The shutter is silent.

Keep the stock image and the backup for recovery.

## Revert

Re-flash the stock `GP_CARDVR_UPGRADE.BIN` the same way.

## Verified

Flashed to a C100: the update completed, the camera booted, photos worked, and the
shutter was silent.

## License

The original code and documentation in this repository are released under the MIT
License (see [`LICENSE`](LICENSE)). The license covers only this repository's original
content. It does not grant any rights to GODOX firmware, firmware-derived assets, or
GODOX trademarks. "GODOX" and "C100" are used descriptively to identify the hardware.
