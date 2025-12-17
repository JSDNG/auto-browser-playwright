"""
Helpers to parse HeyEtsy overlay data from captured HTML.
"""

import re
from html.parser import HTMLParser
from typing import Dict, List, Optional


def _parse_int(value: str) -> Optional[int]:
    try:
        cleaned = value.replace(",", "").replace("+", "").strip()
        if cleaned == "-" or not cleaned:
            return None
        mul = 1
        if cleaned.lower().endswith("k"):
            mul = 1_000
            cleaned = cleaned[:-1]
        elif cleaned.lower().endswith("m"):
            mul = 1_000_000
            cleaned = cleaned[:-1]
        return int(float(cleaned) * mul)
    except Exception:
        return None


class ListingParser(HTMLParser):
    """Grab listing level info (title/url/image) and video flag from the grid."""

    def __init__(self):
        super().__init__()
        self.stack = []
        self.listings: Dict[str, Dict] = {}

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        listing_id = attr.get("data-listing-id")
        if listing_id:
            self.stack.append((tag, listing_id))
            entry = self.listings.setdefault(listing_id, {})
            if tag == "a":
                entry.setdefault("url", attr.get("href"))
                entry.setdefault("title", attr.get("aria-label"))
            classes = (attr.get("class") or "").split()
            if tag == "video" or attr.get("data-listing-card-video") or "video" in classes:
                entry["is_video"] = True
        elif self.stack:
            current_id = self.stack[-1][1]
            entry = self.listings.setdefault(current_id, {})
            if tag == "a":
                entry.setdefault("url", attr.get("href"))
                entry.setdefault("title", attr.get("aria-label"))
            if tag == "img":
                src = attr.get("src") or attr.get("data-src")
                if src:
                    entry.setdefault("image", src)
            classes = (attr.get("class") or "").split()
            if tag == "video" or attr.get("data-listing-card-video") or "video" in classes:
                entry["is_video"] = True

    def handle_endtag(self, tag):
        if self.stack and self.stack[-1][0] == tag:
            self.stack.pop()


class OverlayParser(HTMLParser):
    """Extract HeyEtsy overlay blocks keyed by listing id."""

    def __init__(self):
        super().__init__()
        self.capture_id: Optional[str] = None
        self.depth = 0
        self.buffer: List[str] = []
        self.blocks: Dict[str, str] = {}

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if (
            tag == "div"
            and attr.get("id") == "heyetsy-card-container"
            and attr.get("data-heyetsy-listing-id")
        ):
            self.capture_id = attr["data-heyetsy-listing-id"]
            self.depth = 1
            self.buffer = []
            return
        if self.capture_id:
            self.depth += 1

    def handle_endtag(self, tag):
        if self.capture_id:
            self.depth -= 1
            if self.depth == 0:
                text = " ".join(self.buffer)
                self.blocks[self.capture_id] = re.sub(r"\s+", " ", text).strip()
                self.capture_id = None
                self.buffer = []

    def handle_data(self, data):
        if self.capture_id:
            self.buffer.append(data)


def extract_heyetsy_data(html_text: str) -> List[Dict]:
    listing_parser = ListingParser()
    listing_parser.feed(html_text)

    overlay_parser = OverlayParser()
    overlay_parser.feed(html_text)

    def get_num(label: str, text: str):
        m = re.search(rf"{label}\s*([-\d,.\+KkMm]+)", text)
        return _parse_int(m.group(1)) if m else None

    def get_created(text: str):
        if "Created" not in text:
            return None
        part = text.split("Created", 1)[1]
        if "Updated" in part:
            part = part.split("Updated", 1)[0]
        m = re.search(r"\d{2}/\d{2}/\d{4}", part)
        if m:
            return m.group(0)
        cleaned = part.strip(" :-")
        return cleaned if cleaned else None

    results: List[Dict] = []
    for listing_id, block_text in overlay_parser.blocks.items():
        total_sold = get_num("Total Sold", block_text)
        if total_sold is None or total_sold <= 5:
            continue

        data = {
            "listing_id": listing_id,
            "title": None,
            "url": None,
            "image": None,
            "views_24h": get_num("Views 24H", block_text),
            "sold_24h": get_num("Sold 24H", block_text),
            "total_views": get_num("Total Views", block_text),
            "total_sold": total_sold,
            "favorites": get_num("Favorites", block_text),
            "created": get_created(block_text),
        }

        listing_info = listing_parser.listings.get(listing_id, {})
        if listing_info.get("is_video"):
            continue
        for key in ("title", "url", "image"):
            if listing_info.get(key):
                data[key] = listing_info[key]

        results.append(data)

    return results
