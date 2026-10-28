#!/usr/bin/env python3
"""Package the built fonts and standalone specimen for sharing."""
from pathlib import Path
import hashlib
import shutil
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist"
for filename in ("OFL.txt", "LICENSE-code.txt"):
    shutil.copyfile(ROOT / filename, OUT / filename)
files = ["NeonRiviera-Color.ttf", "NeonRiviera-Mono.ttf", "OFL.txt",
         "LICENSE-code.txt", "PROCITAJ.md", "specimen.html", "preview.png", "title.png"]
checksums = []
for name in files:
    checksums.append(hashlib.sha256((OUT / name).read_bytes()).hexdigest() + "  " + name)
(OUT / "SHA256SUMS").write_text("\n".join(checksums) + "\n")
archive = OUT / "Neon-Riviera.zip"
with ZipFile(archive, "w", ZIP_DEFLATED) as bundle:
    for name in files + ["SHA256SUMS"]:
        bundle.write(OUT / name, "Neon-Riviera/" + name)
with ZipFile(archive) as bundle:
    assert bundle.testzip() is None
    assert len(bundle.namelist()) == len(files) + 1
print(archive, archive.stat().st_size, "bytes; archive integrity OK")
