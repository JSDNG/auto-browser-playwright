"""
Output utilities for saving extracted data.
"""

import json
from pathlib import Path
from typing import Iterable, Mapping, Dict, Any


def save_json(data: Iterable[Mapping], output_file: Path):
    """Save data to JSON file."""
    output_file.write_text(
        json.dumps(list(data), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return output_file


def save_automation_results(results: Dict[str, Any], output_file: Path):
    """
    Save automation results to JSON file.
    
    Args:
        results: Dictionary with keys: success, url, extracted_data, action_data
        output_file: Path to output file
    """
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return output_file
