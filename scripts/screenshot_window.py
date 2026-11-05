#!/usr/bin/env python3
"""Save one X window (not the whole desktop) as a PNG, for lesson screenshots.

  scripts/screenshot_window.py <window-name-substring> <out.png> [--wait SECONDS]

Needs xwininfo and xwd (package x11-apps) on the host, and Pillow. The window must be visible (not minimised).
"""
import re, struct, subprocess, sys, time
from PIL import Image

def find_window(name):
    out = subprocess.run(["xwininfo", "-root", "-tree"], capture_output=True, text=True).stdout
    best = None
    for line in out.splitlines():
        m = re.match(r'\s*(0x[0-9a-f]+) "([^"]*)".*?(\d+)x(\d+)\+', line)
        if m and name.lower() in m.group(2).lower():
            area = int(m.group(3)) * int(m.group(4))
            if area > 10000 and (best is None or area > best[1]):
                best = (m.group(1), area)
    return best[0] if best else None

def xwd_to_png(data, out):
    h = struct.unpack(">25I", data[:100])
    header_size, width, height, bpp = h[0], h[4], h[5], h[11]
    bytes_per_line, ncolors = h[12], h[19]
    assert bpp in (24, 32), f"unsupported bits per pixel: {bpp}"
    pix = data[header_size + ncolors * 12:]
    mode = "BGRA" if bpp == 32 else "BGR"
    img = Image.frombuffer("RGBA" if bpp == 32 else "RGB", (width, height), pix, "raw", mode, bytes_per_line, 1).convert("RGB")
    # Window corners are rounded; the capture fills them with black. Make that black transparent.
    img = img.convert("RGBA"); px = img.load(); r = 30
    for cx, cy in ((0, 0), (width - r, 0), (0, height - r), (width - r, height - r)):
        for x in range(cx, min(cx + r, width)):
            for y in range(cy, min(cy + r, height)):
                if px[x, y][:3] == (0, 0, 0):
                    px[x, y] = (0, 0, 0, 0)
    img.save(out)
    return width, height

def main():
    args = sys.argv[1:]
    wait = 0
    if "--wait" in args:
        i = args.index("--wait"); wait = float(args[i + 1]); del args[i:i + 2]
    name, out = args
    end = time.time() + wait
    win = find_window(name)
    while win is None and time.time() < end:
        time.sleep(1); win = find_window(name)
    if win is None:
        sys.exit(f"no visible window with '{name}' in its title")
    data = subprocess.run(["xwd", "-silent", "-id", win], capture_output=True, check=True).stdout
    print(win, "->", out, "%dx%d" % xwd_to_png(data, out))

main()
