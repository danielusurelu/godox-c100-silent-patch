#!/usr/bin/env python3
"""Silence the photo shutter in a GODOX C100 V1.1.6 firmware image.

Unofficial local patcher. It does not contain or redistribute any firmware data.

The script zeroes the PCM samples of CAMERA.WAV inside the resource archive of a
user-supplied stock GP_CARDVR_UPGRADE.BIN, writes a new output image, and keeps a
backup of the original.

Usage:
    python3 silence_camera.py GP_CARDVR_UPGRADE.BIN [-o GP_CARDVR_UPGRADE_silent.bin]

The output keeps the exact same size, so the camera's updater and the resource table
still work. Flash the output like a normal vendor update.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import struct
import sys
from pathlib import Path

STOCK_SIZE = 0x1C1800
STOCK_SHA256 = "411a553fc58810a1ea5b04ef46819deea317d574246ef5870c31d79d68f95036"
EXPECTED_PATCHED_SHA256 = "592f5a97eaa7ef276cc914c12b2fe14188d208ab8e8faa98b084389cd9330b87"

CAMERA_OFF = 0x171E00
CAMERA_SIZE = 7168


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def find_data_chunk(wav: bytes) -> tuple[int, int]:
    if wav[:4] != b"RIFF" or wav[8:12] != b"WAVE":
        raise ValueError("CAMERA.WAV is not a RIFF/WAVE file")
    offset = 12
    while offset + 8 <= len(wav):
        chunk_id = wav[offset:offset + 4]
        chunk_size = struct.unpack_from("<I", wav, offset + 4)[0]
        if chunk_id == b"data":
            return offset + 8, chunk_size
        offset += 8 + chunk_size + (chunk_size & 1)
    raise ValueError("CAMERA.WAV has no data chunk")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="stock GP_CARDVR_UPGRADE.BIN")
    parser.add_argument(
        "-o", "--output", type=Path,
        help="new output image (default: <input>_silent.bin)",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="continue on an unknown input and overwrite an existing output",
    )
    args = parser.parse_args()

    print("Unofficial GODOX C100 silent-shutter patcher")
    print("Use only on firmware you own. Flashing modified firmware can damage the")
    print("camera and may void the warranty. Provided without warranty.\n")

    if not args.input.is_file():
        sys.exit(f"error: input not found: {args.input}")

    data = bytearray(args.input.read_bytes())
    input_hash = sha256(data)
    if len(data) != STOCK_SIZE or input_hash != STOCK_SHA256:
        if not args.force:
            sys.exit(
                "error: this is not the known stock GODOX C100 V1.1.6 image\n"
                f"  size:   {len(data):#x} (expected {STOCK_SIZE:#x})\n"
                f"  sha256: {input_hash}\n"
                f"  expected: {STOCK_SHA256}\n"
                "Use --force only if you know the layout is the same."
            )
        print("warning: size/hash mismatch, continuing because --force", file=sys.stderr)

    if len(data) < CAMERA_OFF + CAMERA_SIZE:
        sys.exit("error: image is too small for the CAMERA.WAV slot")

    wav = bytes(data[CAMERA_OFF:CAMERA_OFF + CAMERA_SIZE])
    try:
        data_start, data_size = find_data_chunk(wav)
    except ValueError as exc:
        sys.exit(f"error: {exc}")
    if data_start + data_size > CAMERA_SIZE:
        sys.exit("error: CAMERA.WAV data chunk does not fit in its resource slot")

    output = args.output or args.input.with_name(args.input.stem + "_silent.bin")
    if output.resolve() == args.input.resolve():
        sys.exit(
            "error: refusing to overwrite the original firmware; "
            "choose a different output path"
        )
    if output.exists() and not args.force:
        sys.exit(f"error: output already exists: {output}\nUse --force to overwrite it.")

    # Keep the RIFF/fmt/LIST/data headers; zero the samples and the slot padding.
    data[CAMERA_OFF + data_start:CAMERA_OFF + CAMERA_SIZE] = (
        b"\x00" * (CAMERA_SIZE - data_start)
    )

    backup = args.input.with_name(args.input.name + ".bak")
    if backup.exists():
        print(f"backup already exists: {backup}")
    else:
        shutil.copy2(args.input, backup)
        print(f"backup: {backup}")

    output.write_bytes(data)
    output_hash = sha256(data)
    print(f"wrote: {output} ({len(data)} bytes)")
    print(f"sha256: {output_hash}")
    if output_hash == EXPECTED_PATCHED_SHA256:
        print("result: matches the verified silent image")
    else:
        print("result: hash differs from the verified stock image "
              "(expected if you used --force)")
    print("\nNext: rename the output to GP_CARDVR_UPGRADE.BIN and flash it.")
    print("Keep the backup and the stock image for recovery.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
