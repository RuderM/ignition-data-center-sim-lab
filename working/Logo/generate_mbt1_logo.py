#!/usr/bin/env python3
"""Generate a compact MBT1 data center PNG logo without external libraries."""

import base64
import math
import struct
import zlib


SCALE = 4
W = 106
H = 93
SW = W * SCALE
SH = H * SCALE

INK = "#16213e"
MUTED = "#5e6b85"
BLUE = "#2f80ed"
TEAL = "#18a999"
AMBER = "#f5b84b"
BORDER = "#d9e2ef"
SURFACE = "#f7f9fc"
WHITE = "#ffffff"


FONT = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01111", "10000", "10000", "10000", "10000", "10000", "01111"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    " ": ["000", "000", "000", "000", "000", "000", "000"],
}


def rgb(hex_color):
    value = hex_color.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


pixels = [list(rgb(SURFACE)) for _ in range(SW * SH)]


def put(x, y, color):
    if 0 <= x < SW and 0 <= y < SH:
        pixels[y * SW + x] = list(rgb(color))


def rect(x, y, w, h, color):
    x, y, w, h = [int(round(v * SCALE)) for v in (x, y, w, h)]
    for yy in range(max(0, y), min(SH, y + h)):
        for xx in range(max(0, x), min(SW, x + w)):
            pixels[yy * SW + xx] = list(rgb(color))


def rounded_rect(x, y, w, h, r, fill, stroke=None, sw=1):
    x, y, w, h, r = [v * SCALE for v in (x, y, w, h, r)]
    stroke_px = int(sw * SCALE)
    for yy in range(int(y), int(y + h)):
        for xx in range(int(x), int(x + w)):
            dx = max(x + r - xx, 0, xx - (x + w - r))
            dy = max(y + r - yy, 0, yy - (y + h - r))
            inside = dx * dx + dy * dy <= r * r
            if not inside:
                continue
            if stroke and (
                xx < x + stroke_px
                or xx >= x + w - stroke_px
                or yy < y + stroke_px
                or yy >= y + h - stroke_px
                or (dx * dx + dy * dy >= (r - stroke_px) * (r - stroke_px) and (dx or dy))
            ):
                pixels[yy * SW + xx] = list(rgb(stroke))
            else:
                pixels[yy * SW + xx] = list(rgb(fill))


def polygon(points, color):
    pts = [(int(round(x * SCALE)), int(round(y * SCALE))) for x, y in points]
    min_y = max(0, min(y for _, y in pts))
    max_y = min(SH - 1, max(y for _, y in pts))
    for yy in range(min_y, max_y + 1):
        nodes = []
        j = len(pts) - 1
        for i in range(len(pts)):
            xi, yi = pts[i]
            xj, yj = pts[j]
            if (yi < yy <= yj) or (yj < yy <= yi):
                nodes.append(int(xi + (yy - yi) / float(yj - yi) * (xj - xi)))
            j = i
        nodes.sort()
        for i in range(0, len(nodes), 2):
            if i + 1 >= len(nodes):
                break
            for xx in range(max(0, nodes[i]), min(SW, nodes[i + 1])):
                pixels[yy * SW + xx] = list(rgb(color))


def circle(cx, cy, r, color):
    cx, cy, r = [int(round(v * SCALE)) for v in (cx, cy, r)]
    rr = r * r
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) ** 2 + (yy - cy) ** 2 <= rr:
                put(xx, yy, color)


def line(x1, y1, x2, y2, width, color):
    x1, y1, x2, y2, width = [v * SCALE for v in (x1, y1, x2, y2, width)]
    steps = int(max(abs(x2 - x1), abs(y2 - y1))) + 1
    radius = width / 2.0
    for i in range(steps + 1):
        t = i / float(steps or 1)
        cx = x1 + (x2 - x1) * t
        cy = y1 + (y2 - y1) * t
        for yy in range(int(cy - radius), int(cy + radius) + 1):
            for xx in range(int(cx - radius), int(cx + radius) + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= radius * radius:
                    put(xx, yy, color)


def text_width(text, scale):
    width = 0
    for ch in text:
        glyph = FONT[ch]
        width += (len(glyph[0]) + 1) * scale
    return width - scale


def draw_text(text, x, y, scale, color):
    cursor = x
    for ch in text:
        glyph = FONT[ch]
        for row, bits in enumerate(glyph):
            for col, bit in enumerate(bits):
                if bit == "1":
                    rect(cursor + col * scale, y + row * scale, scale, scale, color)
        cursor += (len(glyph[0]) + 1) * scale


def centered_text(text, y, scale, color):
    draw_text(text, (W - text_width(text, scale)) / 2.0, y, scale, color)


rounded_rect(2, 2, 102, 89, 8, WHITE, BORDER, 1)
centered_text("MBT1", 9, 3, INK)

polygon([(18, 31), (64, 31), (75, 41), (75, 70), (18, 70)], INK)
line(64, 31, 64, 42, 3, TEAL)
line(64, 42, 75, 42, 3, TEAL)

for x, y, c in [
    (25, 39, BLUE),
    (39, 39, BLUE),
    (53, 39, BLUE),
    (25, 52, TEAL),
    (39, 52, TEAL),
    (53, 52, TEAL),
]:
    rounded_rect(x, y, 9, 6, 1, c)

polygon([(79, 31), (70, 49), (79, 49), (73, 69), (92, 43), (82, 43), (88, 31)], AMBER)
line(25, 76, 81, 76, 3, BLUE)
circle(25, 76, 4, TEAL)
circle(81, 76, 4, TEAL)
centered_text("DATA CENTER", 83, 1, MUTED)


def downsample():
    out = []
    for y in range(H):
        for x in range(W):
            total = [0, 0, 0]
            for yy in range(SCALE):
                for xx in range(SCALE):
                    r, g, b = pixels[(y * SCALE + yy) * SW + (x * SCALE + xx)]
                    total[0] += r
                    total[1] += g
                    total[2] += b
            count = SCALE * SCALE
            out.append(tuple(int(round(v / count)) for v in total))
    return out


def png_bytes(rgb_pixels):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        for x in range(W):
            raw.extend(rgb_pixels[y * W + x])

    def chunk(kind, data):
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    return b"".join(
        [
            b"\x89PNG\r\n\x1a\n",
            chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)),
            chunk(b"IDAT", zlib.compress(bytes(raw), 9)),
            chunk(b"IEND", b""),
        ]
    )


png = png_bytes(downsample())
with open("working/Logo/mbt1-data-center-logo.png", "wb") as f:
    f.write(png)

uri = "data:image/png;base64," + base64.b64encode(png).decode("ascii")
with open("working/Logo/mbt1-data-center-logo-data-uri.txt", "w") as f:
    f.write(uri + "\n")

print("wrote working/Logo/mbt1-data-center-logo.png")
print("wrote working/Logo/mbt1-data-center-logo-data-uri.txt")
