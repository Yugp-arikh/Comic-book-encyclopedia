# encyclopedia/parsers.py
import csv
import codecs
from typing import List, Dict

def split_semicolon_field(value: str) -> List[str]:
    if not value or value.strip() == "":
        return []
    # split on semicolon and strip whitespace; handle weird unicode separators
    parts = [p.strip() for p in value.split(";") if p.strip() != ""]
    return parts

def parse_isbn(value: str) -> List[str]:
    parts = []
    if not value or value.strip() == "":
        return ["missing"]
    # some are comma-separated
    for p in value.replace(" ", "").split(","):
        p = p.strip()
        if p:
            parts.append(p)
    return parts or ["missing"]

def normalize_text(value: str) -> str:
    if value is None:
        return ""
    # Ensure unicode and remove weird control characters
    return str(value).strip()

def parse_row_to_record(row: Dict[str, str]) -> Dict:
    # Assumes CSV header keys match dataset (Title, Variant titles, Genre, ISBN etc.)
    rec = {}
    rec["bl_record_id"] = normalize_text(row.get("BL record ID") or row.get("BL record id") or row.get("BL record id"))
    rec["title"] = normalize_text(row.get("Title") or row.get("Title "))
    rec["variant_titles"] = split_semicolon_field(row.get("Variant titles") or row.get("Variant titles "))
    rec["authors"] = split_semicolon_field(row.get("Name") or row.get("Name "))
    rec["publication_years"] = split_semicolon_field(row.get("Date of publication") or row.get("Date of publication "))
    rec["genres"] = split_semicolon_field(row.get("Genre") or row.get("Genre "))
    rec["languages"] = split_semicolon_field(row.get("Languages") or row.get("Languages "))
    rec["isbn"] = parse_isbn(row.get("ISBN") or row.get("ISBN "))
    # other fields: keep as dict; also split multi-value fields into lists
    other = {}
    for key in ["Publisher", "Place of publication", "Topics", "Physical description", "Notes"]:
        if key in row:
            val = row.get(key)
            other[key.lower().replace(" ", "_")] = split_semicolon_field(val) if val and ";" in (val or "") else normalize_text(val)
    rec["other_fields"] = other
    return rec
