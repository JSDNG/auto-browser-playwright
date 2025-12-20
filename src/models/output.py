"""
Output utilities for saving extracted data.
"""

import json
from pathlib import Path
from typing import Iterable, Mapping


def save_json(data: Iterable[Mapping], output_file: Path):
    output_file.write_text(
        json.dumps(list(data), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return output_file
