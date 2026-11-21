#!/usr/bin/env python3
"""The World in One Page -- 20 November 2026.

Renders a one-page newspaper front page (1024x1024 PNG) summarising six
verified world-news stories from Friday 20 November 2026.

Pure standard library: os, struct, sys, zlib, math. No network, no clock,
no randomness -- running it twice produces byte-identical output.

Usage:  MAKEFUN_OUTPUT_DIR=out python3 main.py
Writes entry.png into MAKEFUN_OUTPUT_DIR (default "out").
"""

import math
import os
import struct
import sys
import zlib

# ---------------------------------------------------------------------------
# 5x7 bitmap font, designed for this program.
# Each glyph is 7 rows; each row is a 5-bit integer, bit 4 = leftmost pixel.
# ---------------------------------------------------------------------------

FONT_UPPER = {
    "A": (0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "B": (0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110),
    "C": (0b01110, 0b10001, 0b10000, 0b10000, 0b10000, 0b10001, 0b01110),
    "D": (0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b11110),
    "E": (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111),
    "F": (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000),
    "G": (0b01110, 0b10001, 0b10000, 0b10111, 0b10001, 0b10001, 0b01111),
    "H": (0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "I": (0b01110, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "J": (0b00111, 0b00010, 0b00010, 0b00010, 0b00010, 0b10010, 0b01100),
    "K": (0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001),
    "L": (0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111),
    "M": (0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001),
    "N": (0b10001, 0b11001, 0b10101, 0b10011, 0b10001, 0b10001, 0b10001),
    "O": (0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "P": (0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000),
    "Q": (0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101),
    "R": (0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001),
    "S": (0b01111, 0b10000, 0b10000, 0b01110, 0b00001, 0b00001, 0b11110),
    "T": (0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100),
    "U": (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "V": (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100),
    "W": (0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b11011, 0b10001),
    "X": (0b10001, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b10001),
    "Y": (0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100),
    "Z": (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111),
}

FONT_DIGITS = {
    "0": (0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110),
    "1": (0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "2": (0b01110, 0b10001, 0b00001, 0b00110, 0b01000, 0b10000, 0b11111),
    "3": (0b11111, 0b00010, 0b00100, 0b00010, 0b00001, 0b10001, 0b01110),
    "4": (0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010),
    "5": (0b11111, 0b10000, 0b11110, 0b00001, 0b00001, 0b10001, 0b01110),
    "6": (0b00110, 0b01000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110),
    "7": (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b01000, 0b01000),
    "8": (0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110),
    "9": (0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00010, 0b01100),
}

FONT_PUNCT = {
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b01100, 0b01100),
    ",": (0b00000, 0b00000, 0b00000, 0b00000, 0b01100, 0b00100, 0b01000),
    ":": (0b00000, 0b01100, 0b01100, 0b00000, 0b01100, 0b01100, 0b00000),
    ";": (0b00000, 0b01100, 0b01100, 0b00000, 0b01100, 0b00100, 0b01000),
    "!": (0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00000, 0b00100),
    "?": (0b01110, 0b10001, 0b00001, 0b00110, 0b00100, 0b00000, 0b00100),
    "-": (0b00000, 0b00000, 0b00000, 0b01110, 0b00000, 0b00000, 0b00000),
    "'": (0b00100, 0b00100, 0b01000, 0b00000, 0b00000, 0b00000, 0b00000),
    '"': (0b01010, 0b01010, 0b01010, 0b00000, 0b00000, 0b00000, 0b00000),
    "(": (0b00010, 0b00100, 0b01000, 0b01000, 0b01000, 0b00100, 0b00010),
    ")": (0b01000, 0b00100, 0b00010, 0b00010, 0b00010, 0b00100, 0b01000),
    "/": (0b00001, 0b00010, 0b00010, 0b00100, 0b01000, 0b01000, 0b10000),
    "%": (0b11001, 0b11010, 0b00010, 0b00100, 0b01000, 0b01011, 0b10011),
    "$": (0b00100, 0b01111, 0b10100, 0b01110, 0b00101, 0b11110, 0b00100),
    "&": (0b01100, 0b10010, 0b10100, 0b01000, 0b10101, 0b10010, 0b01101),
    "+": (0b00000, 0b00100, 0b00100, 0b11111, 0b00100, 0b00100, 0b00000),
    "=": (0b00000, 0b00000, 0b11111, 0b00000, 0b11111, 0b00000, 0b00000),
    "@": (0b01110, 0b10001, 0b10111, 0b10101, 0b10110, 0b10000, 0b01110),
    "#": (0b01010, 0b01010, 0b11111, 0b01010, 0b11111, 0b01010, 0b01010),
    "*": (0b00000, 0b10101, 0b01110, 0b11111, 0b01110, 0b10101, 0b00000),
    "_": (0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b11111),
    "[": (0b01110, 0b01000, 0b01000, 0b01000, 0b01000, 0b01000, 0b01110),
    "]": (0b01110, 0b00010, 0b00010, 0b00010, 0b00010, 0b00010, 0b01110),
    "<": (0b00010, 0b00100, 0b01000, 0b10000, 0b01000, 0b00100, 0b00010),
    ">": (0b01000, 0b00100, 0b00010, 0b00001, 0b00010, 0b00100, 0b01000),
    "|": (0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100),
    "~": (0b00000, 0b00000, 0b01101, 0b10110, 0b00000, 0b00000, 0b00000),
    "^": (0b00100, 0b01010, 0b10001, 0b00000, 0b00000, 0b00000, 0b00000),
    "`": (0b01000, 0b00100, 0b00010, 0b00000, 0b00000, 0b00000, 0b00000),
    "{": (0b00110, 0b01000, 0b01000, 0b11110, 0b01000, 0b01000, 0b00110),
    "}": (0b01100, 0b00010, 0b00010, 0b01111, 0b00010, 0b00010, 0b01100),
    "\\": (0b10000, 0b01000, 0b01000, 0b00100, 0b00010, 0b00010, 0b00001),
    # bullet, drawn as a solid 3x3 block in the middle rows
    "\u2022": (0b00000, 0b00000, 0b01110, 0b01110, 0b01110, 0b00000, 0b00000),
}

FONT_LOWER = {
    "a": (0b00000, 0b00000, 0b01110, 0b00001, 0b01111, 0b10001, 0b01111),
    "b": (0b10000, 0b10000, 0b11110, 0b10001, 0b10001, 0b10001, 0b11110),
    "c": (0b00000, 0b00000, 0b01110, 0b10000, 0b10000, 0b10001, 0b01110),
    "d": (0b00001, 0b00001, 0b01111, 0b10001, 0b10001, 0b10001, 0b01111),
    "e": (0b00000, 0b00000, 0b01110, 0b10001, 0b11111, 0b10000, 0b01110),
    "f": (0b00110, 0b01001, 0b01000, 0b11110, 0b01000, 0b01000, 0b01000),
    "g": (0b00000, 0b01111, 0b10001, 0b10001, 0b01111, 0b00001, 0b01110),
    "h": (0b10000, 0b10000, 0b11110, 0b10001, 0b10001, 0b10001, 0b10001),
    "i": (0b00100, 0b00000, 0b01100, 0b00100, 0b00100, 0b00100, 0b01110),
    "j": (0b00010, 0b00000, 0b00110, 0b00010, 0b00010, 0b10010, 0b01100),
    "k": (0b10000, 0b10000, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010),
    "l": (0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "m": (0b00000, 0b00000, 0b11010, 0b10101, 0b10101, 0b10101, 0b10101),
    "n": (0b00000, 0b00000, 0b11110, 0b10001, 0b10001, 0b10001, 0b10001),
    "o": (0b00000, 0b00000, 0b01110, 0b10001, 0b10001, 0b10001, 0b01110),
    "p": (0b00000, 0b00000, 0b11110, 0b10001, 0b10001, 0b11110, 0b10000),
    "q": (0b00000, 0b00000, 0b01111, 0b10001, 0b10001, 0b01111, 0b00001),
    "r": (0b00000, 0b00000, 0b10110, 0b11001, 0b10000, 0b10000, 0b10000),
    "s": (0b00000, 0b00000, 0b01111, 0b10000, 0b01110, 0b00001, 0b11110),
    "t": (0b01000, 0b01000, 0b11100, 0b01000, 0b01000, 0b01001, 0b00110),
    "u": (0b00000, 0b00000, 0b10001, 0b10001, 0b10001, 0b10011, 0b01101),
    "v": (0b00000, 0b00000, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100),
    "w": (0b00000, 0b00000, 0b10001, 0b10101, 0b10101, 0b10101, 0b01010),
    "x": (0b00000, 0b00000, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001),
    "y": (0b00000, 0b00000, 0b10001, 0b10001, 0b01111, 0b00001, 0b01110),
    "z": (0b00000, 0b00000, 0b11111, 0b00010, 0b00100, 0b01000, 0b11111),
}

FONT = {}
FONT.update(FONT_UPPER)
FONT.update(FONT_LOWER)
FONT.update(FONT_DIGITS)
FONT.update(FONT_PUNCT)

# ---------------------------------------------------------------------------
# Canvas: an RGB image held as one flat bytearray, with tiny drawing helpers.
# ---------------------------------------------------------------------------

PAPER = (247, 243, 232)   # warm newsprint
INK = (20, 20, 20)        # near-black ink
RED = (163, 18, 18)       # headline accent red
BLUE = (27, 58, 107)      # deep blue for kickers and rules
GREY = (90, 86, 78)       # muted grey for the footer


class Canvas:
    def __init__(self, width, height, colour):
        self.w = width
        self.h = height
        self.px = bytearray(width * height * 3)
        r, g, b = colour
        for i in range(0, len(self.px), 3):
            self.px[i] = r
            self.px[i + 1] = g
            self.px[i + 2] = b

    def set(self, x, y, colour):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = colour

    def fill_rect(self, x, y, w, h, colour):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        r, g, b = colour
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i] = r
                self.px[i + 1] = g
                self.px[i + 2] = b

    def hline(self, x, y, w, colour, thick=1):
        self.fill_rect(x, y, w, thick, colour)

    def vline(self, x, y, h, colour, thick=1):
        self.fill_rect(x, y, thick, h, colour)

    def circle(self, cx, cy, rad, colour):
        # Mid-point circle outline, plus a horizontal equator and two
        # meridian ellipses, so it reads as a small globe.
        x = 0
        y = rad
        d = 1 - rad
        while x <= y:
            for sx, sy in ((x, y), (y, x), (-x, y), (-y, x),
                           (x, -y), (y, -x), (-x, -y), (-y, -x)):
                self.set(cx + sx, cy + sy, colour)
            if d < 0:
                d += 2 * x + 3
            else:
                d += 2 * (x - y) + 5
                y -= 1
            x += 1
        # equator
        for dx in range(-rad, rad + 1):
            dy = int(round(math.sqrt(max(0, rad * rad - dx * dx)) * 0.0))
            self.set(cx + dx, cy + dy, colour)
        # meridians: two vertical ellipses
        for dy in range(-rad, rad + 1):
            half = int(round(math.sqrt(max(0, rad * rad - dy * dy))))
            for frac, sign in ((0.45, 1), (0.45, -1)):
                self.set(cx + sign * int(round(half * frac)), cy + dy, colour)
            self.set(cx + int(round(half * 0.0)), cy + dy, colour)


def text_width(text, scale):
    """Pixel width of text at the given scale (6 px advance per glyph)."""
    return len(text) * 6 * scale


def draw_text(cv, text, x, y, scale, colour):
    """Draw text with the 5x7 font; unknown glyphs become blanks."""
    cx = x
    for ch in text:
        glyph = FONT.get(ch)
        if glyph:
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        cv.fill_rect(cx + col * scale, y + row * scale,
                                     scale, scale, colour)
        cx += 6 * scale
    return cx


def draw_text_centred(cv, text, cx, y, scale, colour):
    draw_text(cv, text, cx - text_width(text, scale) // 2, y, scale, colour)


def wrap_text(text, max_width, scale):
    """Greedy word wrap; returns a list of lines fitting max_width px."""
    unit = 6 * scale
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if len(trial) * unit <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_para(cv, text, x, y, max_width, scale, colour, leading=None):
    """Draw a wrapped paragraph; returns the y just below the last line."""
    if leading is None:
        leading = 7 * scale + 3
    for line in wrap_text(text, max_width, scale):
        draw_text(cv, line, x, y, scale, colour)
        y += leading
    return y


# ---------------------------------------------------------------------------
# Minimal PNG encoder (truecolour, filter 0, fixed compression level).
# ---------------------------------------------------------------------------

def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(cv, path):
    width, height = cv.w, cv.h
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)  # filter: none
        raw += cv.px[y * stride:(y + 1) * stride]
    png = (b"\x89PNG\r\n\x1a\n"
           + _chunk(b"IHDR", ihdr)
           + _chunk(b"IDAT", zlib.compress(bytes(raw), 6))
           + _chunk(b"IEND", b""))
    with open(path, "wb") as fh:
        fh.write(png)
    return len(png)


# ---------------------------------------------------------------------------
# Content: six verified stories from Friday 20 November 2026.
# Sources: BBC News, Reuters, Associated Press, Council on Foreign Relations.
# ---------------------------------------------------------------------------

LEAD = {
    "kicker": "WAR IN EUROPE",
    "headline": ["RUSSIA HITS KYIV BRIDGES", "MISSILES LAND IN POLAND"],
    "body": ("Russia fired more than 400 drones and 110 missiles at Ukraine "
             "on Friday, hitting three bridges across the Dnipro in Kyiv and "
             "killing at least eight people. Two Russian missiles and a "
             "suspected drone fell inside Poland, a NATO member, with no "
             "casualties. Kyiv said its defences downed 462 targets."),
}

STORIES = [
    {
        "kicker": "DIPLOMACY",
        "headline": "TRUMP, XI AND PUTIN PLEDGE PEACE AFTER SHENZHEN TALKS",
        "body": ("Trump, Xi and Putin held their first three-way meeting in "
                 "Shenzhen and issued a joint declaration on peace and "
                 "stability. Analysts said the spectacle outran the "
                 "substance."),
    },
    {
        "kicker": "EUROPE",
        "headline": "UK AND EU AGREE NEW DEAL ON FOOD, EMISSIONS, YOUTH",
        "body": ("Britain and the European Union agreed a deal on Friday "
                 "covering food exports, emissions trading and a youth "
                 "experience scheme. London said it would explore even "
                 "closer ties."),
    },
    {
        "kicker": "CLIMATE",
        "headline": "COP31 TALKS DEADLOCK OVER FOSSIL FUELS",
        "body": ("UN climate talks in Antalya, Turkey, stalled on Friday as "
                 "negotiators failed to agree how to address fossil fuels "
                 "in the draft deal. Activists denounced the draft as the "
                 "talks ran into the night."),
    },
    {
        "kicker": "SCIENCE",
        "headline": "AI CLAIMS PROOF OF MATH'S GREATEST PRIZE PUZZLE",
        "body": ("Anthropic mathematician Levent Alpoge said on Friday that, "
                 "working with the AI model Claude, he has found a proof of "
                 "the Riemann hypothesis, unsolved since 1859. The "
                 "17-million-line proof is still being checked."),
    },
    {
        "kicker": "JUSTICE",
        "headline": "MYANMAR CALLS UN GENOCIDE RULING 'UNFAIR'",
        "body": ("Myanmar on Friday rejected the International Court of "
                 "Justice ruling that its forces committed genocide against "
                 "the Rohingya in 2017. The court, in a first for a state, "
                 "ordered reparations and the safe return of refugees."),
    },
]

NUMBERS = ("BY THE NUMBERS:  462 targets intercepted over Ukraine  "
           "\u2022  10,000 Rohingya killed, the court found  \u2022  "
           "250,000 pages in the AI maths proof")


# ---------------------------------------------------------------------------
# Page layout: a one-page newspaper front page, 1024 x 1024.
# ---------------------------------------------------------------------------

W, H = 1024, 1024
MARGIN = 28
CONTENT = W - 2 * MARGIN  # 968
IX = MARGIN + 6           # inner text inset, clear of the frame
IW = CONTENT - 12         # inner text width


def draw_story_block(cv, story, x, y, width, head_scale, body_scale):
    draw_text(cv, story["kicker"], x, y, 2, RED)
    y += 7 * 2 + 8
    for line in wrap_text(story["headline"], width, head_scale):
        draw_text(cv, line, x, y, head_scale, INK)
        y += 7 * head_scale + 4
    y += 2
    y = draw_para(cv, story["body"], x, y, width, body_scale, INK)
    return y


def build_page():
    cv = Canvas(W, H, PAPER)
    # outer frame
    cv.hline(MARGIN, MARGIN, CONTENT, INK, 3)
    cv.hline(MARGIN, H - MARGIN, CONTENT, INK, 3)
    cv.vline(MARGIN, MARGIN, H - 2 * MARGIN, INK, 3)
    cv.vline(W - MARGIN, MARGIN, H - 2 * MARGIN, INK, 3)

    # masthead: small globes flanking the title
    cv.circle(72, 66, 26, BLUE)
    cv.circle(W - 72, 66, 26, BLUE)
    draw_text_centred(cv, "THE WORLD IN ONE PAGE", W // 2, 34, 5, INK)
    draw_text_centred(cv, "FRIDAY 20 NOVEMBER 2026", W // 2, 84, 3, RED)
    draw_text_centred(
        cv, "SIX STORIES FROM ONE DAY - THE WHOLE WORLD ON A SINGLE PAGE",
        W // 2, 116, 2, GREY)
    cv.hline(MARGIN + 10, 142, CONTENT - 20, INK, 2)
    cv.hline(MARGIN + 10, 147, CONTENT - 20, INK, 1)

    # lead story
    y = 164
    draw_text(cv, LEAD["kicker"], IX, y, 2, RED)
    y += 7 * 2 + 8
    for line in LEAD["headline"]:
        draw_text(cv, line, IX, y, 4, INK)
        y += 7 * 4 + 4
    y += 4
    y = draw_para(cv, LEAD["body"], IX, y, IW, 2, INK)
    cv.hline(MARGIN, y + 8, CONTENT, INK, 2)

    # grid: stories 1-2, 3-4 side by side; story 5 full width
    col_w = (IW - 20) // 2
    grid_y = y + 26
    row_h = 200
    draw_story_block(cv, STORIES[0], IX, grid_y, col_w, 3, 2)
    draw_story_block(cv, STORIES[1], IX + col_w + 20, grid_y,
                     col_w, 3, 2)
    cv.vline(IX + col_w + 10, grid_y, row_h, GREY, 1)
    cv.hline(MARGIN, grid_y + row_h, CONTENT, GREY, 1)
    draw_story_block(cv, STORIES[2], IX, grid_y + row_h + 14,
                     col_w, 3, 2)
    draw_story_block(cv, STORIES[3], IX + col_w + 20,
                     grid_y + row_h + 14, col_w, 3, 2)
    cv.vline(IX + col_w + 10, grid_y + row_h + 14, row_h, GREY, 1)
    cv.hline(MARGIN, grid_y + 2 * row_h + 14, CONTENT, GREY, 1)

    y5 = grid_y + 2 * row_h + 28
    draw_story_block(cv, STORIES[4], IX, y5, IW, 3, 2)

    # numbers strip + footer
    strip_y = H - MARGIN - 78
    cv.fill_rect(MARGIN, strip_y, CONTENT, 2, BLUE)
    draw_para(cv, NUMBERS, IX, strip_y + 10, IW, 2, BLUE)
    cv.hline(MARGIN, H - MARGIN - 30, CONTENT, INK, 1)
    draw_text(cv, "Sources: BBC News, Reuters, Associated Press, Council on "
                  "Foreign Relations - 20 November 2026",
              IX, H - MARGIN - 22, 1, GREY)
    return cv


def main(argv):
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    size = write_png(build_page(), path)
    print("wrote %s (%d bytes)" % (path, size))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
