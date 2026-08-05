#!/usr/bin/env python3
"""Render a captioned TradeProof demo MP4 from public, verified testnet evidence."""

from __future__ import annotations

import argparse
from pathlib import Path

import imageio
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
W, H, FPS = 1280, 720, 24
BG = "#07111f"
PANEL = "#102138"
CYAN = "#5bc8f5"
WHITE = "#e7efff"
MUTED = "#afc2dc"
GREEN = "#43d19e"
AMBER = "#f6c453"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(name, size)


def blank() -> Image.Image:
    return Image.new("RGB", (W, H), BG)


def wrapped(draw: ImageDraw.ImageDraw, text: str, x: int, y: int, width: int, style: ImageFont.FreeTypeFont, fill: str, gap: int = 10) -> int:
    words, line, lines = text.split(), "", []
    for word in words:
        trial = f"{line} {word}".strip()
        if draw.textbbox((0, 0), trial, font=style)[2] > width and line:
            lines.append(line); line = word
        else:
            line = trial
    if line: lines.append(line)
    for line in lines:
        draw.text((x, y), line, font=style, fill=fill)
        y += int(style.size) + gap
    return y


def slide(title: str, lines: list[tuple[str, str]], footer: str = "ARC TESTNET · SYNTHETIC INVOICES · TEST-USDC ONLY") -> Image.Image:
    im = blank(); d = ImageDraw.Draw(im)
    d.rounded_rectangle((60, 54, 1220, 666), radius=24, fill=PANEL, outline="#234463", width=2)
    d.text((105, 98), title, font=font(46, True), fill=WHITE)
    y = 198
    for text, color in lines:
        y = wrapped(d, text, 110, y, 1040, font(28), color) + 22
    d.text((105, 620), footer, font=font(16, True), fill=CYAN)
    return im


def ui_slide() -> Image.Image:
    screenshot = Image.open(ROOT / "docs/demo/ui-form.png").convert("RGB")
    screenshot.thumbnail((1120, 630))
    im = blank(); im.paste(screenshot, ((W - screenshot.width) // 2, (H - screenshot.height) // 2))
    return im


def main() -> None:
    p = argparse.ArgumentParser(description="Render TradeProof captioned evidence video")
    p.add_argument("--refund-tx", required=True)
    p.add_argument("--output", default="docs/demo/tradeproof-demo.mp4")
    args = p.parse_args()

    complete_tx = "0x793f99fa68c20dbeb2e0cba9342f5d733d1b97ed9a693c1f8e87c470e83aa28b"
    slides = [
        (slide("TradeProof Escrow", [("A synthetic UAE-to-global SME invoice workflow with proof-backed settlement paths.", WHITE), ("Educational demo only — Arc Testnet and test-USDC; no custody, real invoice or mainnet activity.", AMBER)]), 6),
        (ui_slide(), 7),
        (slide("Deterministic instruction", [("Synthetic invoice → canonical SHA-256 invoice hash", CYAN), ("Delivery evidence → independent SHA-256 proof hash", "#b69cff"), ("The UI never asks for a wallet, private key or real funds.", WHITE)]), 7),
        (slide("Job A · proof-backed completion", [("Job ID 168870 · bounded at 1 test-USDC", GREEN), ("create → set budget → fund → submit delivery proof → complete", WHITE), (f"Arcscan completion: {complete_tx[:10]}…{complete_tx[-6:]} (full link in evidence)", MUTED)]), 10),
        (slide("Job B · expiry and refund", [("Job ID 168872 · separate 1 test-USDC job", GREEN), ("create → set budget → fund → expiry → claim refund", WHITE), (f"Arcscan refund: {args.refund_tx[:10]}…{args.refund_tx[-6:]} (full link in evidence)", MUTED)]), 10),
        (slide("Verifiable, constrained prototype", [("Public repo: github.com/Scarpo-gh/tradeproof-escrow", CYAN), ("Two isolated Arc Testnet job lifecycles; secrets and recovery material are excluded from the repository.", WHITE), ("TradeProof is not a production payment, credit, KYC/AML or custody service.", AMBER)]), 7),
    ]
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    writer = imageio.get_writer(out, fps=FPS, codec="libx264", pixelformat="yuv420p")
    try:
        for image, seconds in slides:
            frame = np.asarray(image)
            for _ in range(int(seconds * FPS)):
                writer.append_data(frame)
    finally:
        writer.close()
    print(out)


if __name__ == "__main__":
    main()
