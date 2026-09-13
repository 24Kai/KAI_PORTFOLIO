"""Regenerate the public, text-only casebook from the same website content."""
import json
from pathlib import Path
from casebook import full_casebook

if __name__ == '__main__':
    root = Path(__file__).resolve().parent
    content = json.loads((root/'portfolio_content.json').read_text(encoding='utf-8-sig'))
    (root/'CASEBOOK.md').write_text(full_casebook(content),encoding='utf-8')
