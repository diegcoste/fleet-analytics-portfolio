"""Escaneo de cadenas sensibles antes de publicar.

    python scripts/scan_sensitive.py            # sale con código 1 si encuentra algo
    SCAN_EXTRA="palabra1,palabra2" python scripts/scan_sensitive.py

Busca: llaves/API keys, correos, VINs de 17 caracteres, contraseñas y términos extra
definidos en la variable de entorno SCAN_EXTRA (útil para nombres internos que no deben
quedar escritos en el repo).
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", ".venv", "__pycache__", "out", ".pytest_cache", ".ruff_cache"}
SKIP_FILES = {"scan_sensitive.py"}

PATTERNS = {
    "api_key": re.compile(r"(api[_-]?key|token|secret)\s*[:=]\s*['\"][A-Za-z0-9]{16,}['\"]", re.IGNORECASE),
    "password": re.compile(r"password\s*[:=]\s*\S{6,}", re.IGNORECASE),
    "email": re.compile(r"[A-Za-z0-9._%+-]+@(?!example\.com|anthropic\.com)[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "vin": re.compile(r"\b[A-HJ-NPR-Z0-9]{17}\b"),
}
EXTRA = [t.strip().lower() for t in os.getenv("SCAN_EXTRA", "").split(",") if t.strip()]


def main() -> int:
    hits = []
    for p in ROOT.rglob("*"):
        if p.is_dir() or any(part in SKIP_DIRS for part in p.parts) or p.name in SKIP_FILES:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for n, line in enumerate(text.splitlines(), 1):
            for name, rx in PATTERNS.items():
                if rx.search(line):
                    hits.append((p.relative_to(ROOT), n, name, line.strip()[:120]))
            low = line.lower()
            for t in EXTRA:
                if t in low:
                    hits.append((p.relative_to(ROOT), n, f"extra:{t}", line.strip()[:120]))
    for h in hits:
        print(f"{h[0]}:{h[1]}  [{h[2]}]  {h[3]}")
    print(f"\n{len(hits)} hallazgo(s)")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
