# Silent shutter patch — GODOX C100 V1.1.6

`silence_camera.py` is an **unofficial local patcher** for a stock GODOX C100 V1.1.6
image. The repository does not distribute the firmware; you supply your own
`GP_CARDVR_UPGRADE.BIN`.

> **Legal and safety notice**
>
> - Unofficial project; not affiliated with, authorized by, sponsored by, or endorsed by
>   GODOX.
> - This repository does not include or distribute GODOX firmware.
> - Download the official firmware directly from GODOX and supply it locally.
> - The script modifies a local copy of your own firmware.
> - Flashing modified firmware can damage the camera and may void the warranty.
> - Provided without warranty.
> - Removing audible feedback means the camera may operate silently; follow applicable
>   laws and obtain consent before photographing or recording people.

> **Tested only on:** the stock GODOX C100 **V1.1.6** image with SHA-256
> `411a553fc58810a1ea5b04ef46819deea317d574246ef5870c31d79d68f95036`.
> The patcher checks this hash and refuses other images unless `--force`; the CAMERA.WAV
> offsets may differ on other firmware versions.

## Requirements

- Python 3.8+
- The stock V1.1.6 image:
  - size `0x1C1800` (1,841,152 bytes)
  - SHA-256 `411a553fc58810a1ea5b04ef46819deea317d574246ef5870c31d79d68f95036`

## Apply the patch

```sh
python3 silence_camera.py GP_CARDVR_UPGRADE.BIN -o GP_CARDVR_UPGRADE_silent.bin
```

The script:

- verifies the stock size and SHA-256;
- writes the patched image to a **new** output path and refuses to overwrite the input;
- creates a backup (`<input>.bak`) before writing the output;
- refuses to overwrite an existing output unless `--force` is passed.

Expected output:

```
Unofficial GODOX C100 silent-shutter patcher
...
backup: GP_CARDVR_UPGRADE.BIN.bak
wrote: GP_CARDVR_UPGRADE_silent.bin (1841152 bytes)
sha256: 592f5a97eaa7ef276cc914c12b2fe14188d208ab8e8faa98b084389cd9330b87
result: matches the verified silent image
```

The output keeps the exact same size, so the resource table, the next file's offset, and
the camera's updater size check still work.

## Flash

1. Rename `GP_CARDVR_UPGRADE_silent.bin` to `GP_CARDVR_UPGRADE.BIN`.
2. Copy it to the **root** of a FAT32 or exFAT SD card.
3. With the camera off, insert the card and power on.
4. The LED flashes while the image is written (~10 s), then the camera powers off.
5. Power on again. The shutter is silent.

The updater deletes the file after a successful write and recreates a version file.

## What the patch changes

Only the PCM samples of `CAMERA.WAV` (resource slot at `0x171E00`, 7,168 bytes). The RIFF
/ `fmt ` / `LIST` / `data` headers are preserved; the samples and slot padding are zeroed.
Nothing else in the image is touched.

## Revert

Re-flash the stock `GP_CARDVR_UPGRADE.BIN` the same way.

## License

The patcher and documentation are MIT-licensed (see [`../LICENSE`](../LICENSE)). The
license covers only this repository's original content; it does not cover GODOX firmware
or GODOX trademarks.
