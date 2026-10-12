"""Stamp README image URLs with a content hash: ./assets/x.svg -> ./assets/x.svg?v=<sha8>.

Browsers and GitHub's CDN cache images by URL, so an updated SVG kept showing the old
(static) version. A hash of the file contents changes the URL exactly when the file
changes. Run after any asset build; the daily Action runs it too.
"""
from pathlib import Path
import hashlib
import re

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / 'README.md'
PATTERN = re.compile(r'((?:src|srcset)=")(\./assets/[^"?]+)(?:\?v=[0-9a-f]+)?(")')


def stamp(match):
    path = ROOT / match.group(2)
    if not path.exists():
        raise SystemExit(f'missing asset: {match.group(2)}')
    digest = hashlib.sha256(path.read_bytes()).hexdigest()[:8]
    return f'{match.group(1)}{match.group(2)}?v={digest}{match.group(3)}'


text = README.read_text()
stamped, count = PATTERN.subn(stamp, text)
if stamped != text:
    README.write_text(stamped)
print(f'Stamped {count} asset URLs')
