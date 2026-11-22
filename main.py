#!/usr/bin/env python3
"""Hand in the entry: copy the shipped entry.png to the output directory.

Standard library only. The image itself is rendered locally by render.py
(committed alongside) and shipped in the repository as entry.png; this
program simply carries it, byte for byte, from the bot directory to
$MAKEFUN_OUTPUT_DIR/entry.png, identically on every run.
"""
import os
import shutil


def main():
    bot_dir = os.environ.get("MAKEFUN_BOT_DIR", os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(os.path.join(bot_dir, "entry.png"),
                    os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
