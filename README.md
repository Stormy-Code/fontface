# Neon Riviera

**[Preuzmi fontove i upute — ZIP](https://github.com/Stormy-Code/fontface/raw/refs/heads/main/dist/Neon-Riviera.zip)**

Raspakiraj ZIP pa instaliraj `NeonRiviera-Color.ttf` ili `NeonRiviera-Mono.ttf`.
Paket uključuje hrvatske znakove, interaktivni pregled, upute i licencu za dijeljenje.
Boje zahtijevaju aplikaciju s podrškom za COLRv1; za ostale koristi Mono.

Installable neon display fonts inspired by the supplied **210GB** artwork.
Heavy italic Montserrat outlines, pink/cyan/gold/violet chrome gradients,
luminous vector rims and purple extrusion. This is an interpretation of the
reference, not an exact recovery of its original typeface.

## Deliverables

Open `dist/specimen.html` in modern Chrome/Edge for a live text specimen.
Install `dist/NeonRiviera-Color.ttf` for COLRv1-aware applications or
`dist/NeonRiviera-Mono.ttf` for conventional TrueType support.
See `dist/PROCITAJ.md` for Croatian installation and sharing instructions.

## Rebuild

Use the existing checkout; no Git worktree is needed.

```sh
cd /workspace/fontface
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/build_fonts.py
```

The checked-in upstream source is Montserrat's variable italic font, instantiated
at weight 900. Its checksum is checked by the build. Dependencies: Python 3.10+
and fonttools 4.61.1. No network access is needed once dependencies are installed.
The build leaves upstream source untouched, subsets Latin/Latin Extended-A,
retains OpenType shaping and emits independent renamed families.

Optional browser verification and preview regeneration (requires `playwright`
and `/usr/bin/chromium`): `python scripts/check_preview.py`. This checks font
loading, the Croatian sample, both controls, and mobile overflow. It uses a
temporary loopback server and stops it when finished. To refresh the shareable
ZIP after building and rendering: `python scripts/package_fonts.py`.

Source: https://github.com/google/fonts/tree/main/ofl/montserrat

COLRv1 palettes are fixed per character, not position in a word. Digit glyphs
are pink, G/g cyan, B/b gold, and other characters cycle through four palettes.
Monochrome fallback contains the base outlines, without the color effects.
Neither font includes the source photograph or its scene.

## License

Font files, including derivatives, are under SIL OFL 1.1; see `OFL.txt`.
Upstream copyright is retained in the font and source license.
Build tooling and HTML specimen: MIT; see `LICENSE-code.txt`.
