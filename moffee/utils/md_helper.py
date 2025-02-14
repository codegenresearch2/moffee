import os
import re
from typing import Optional
from urllib.parse import urljoin, urlparse

def is_comment(line: str) -> bool:
    return bool(re.match(r"^\s*<!--.*-->\s*$", line))

def get_header_level(line: str) -> int:
    match = re.match(r"^(#{1,6})\s", line)
    return len(match.group(1)) if match else 0

def is_empty(line: str) -> bool:
    return is_comment(line) or line.strip() == ""

def is_divider(line: str, type: Optional[str] = None) -> bool:
    stripped_line = line.strip()
    if len(stripped_line) < 3:
        return False
    if type is None:
        type = "-*_"
    assert type in "-*_", "type must be either '*', '-' or '_'"
    return all(char in type for char in stripped_line) and any(char * 3 in stripped_line for char in type)

def contains_image(line: str) -> bool:
    return bool(re.search(r"!\[.*?\]\(.*?\)", line))

def contains_deco(line: str) -> bool:
    return bool(re.match(r"^\s*@\(.*?\)\s*$", line))

def extract_title(document: str) -> Optional[str]:
    match = re.search(r"^(#|##)\s+(.*?)(?:\n|$)", document, re.MULTILINE)
    return match.group(2).strip() if match else None

def rm_comments(document: str) -> str:
    document = re.sub(r"<!--[\s\S]*?-->", "", document)
    document = re.sub(r"^\s*%%.*$", "", document, flags=re.MULTILINE)
    return document.strip()

def is_divider_syntax(line: str) -> bool:
    # Improved divider syntax
    return bool(re.match(r"^\s*[*-_]{3,}\s*$", line))

def consistent_header_levels(document: str) -> str:
    # Consistent handling of header levels
    document = re.sub(r"^###(.*)", r"##\1", document, flags=re.MULTILINE)
    document = re.sub(r"^#(.*)", r"##\1", document)
    return document