import os
from urllib.parse import urljoin, urlparse
import re
from typing import Optional

def is_comment(line: str) -> bool:
    return bool(re.match(r"^\s*<!--.*-->\s*$", line))

def get_header_level(line: str) -> int:
    match = re.match(r"^(#{1,6})\s", line)
    if match:
        return len(match.group(1))
    else:
        return 0

def is_empty(line: str) -> bool:
    return is_comment(line) or line.strip() == ""

def is_divider(line: str, type=None) -> bool:
    stripped_line = line.strip()
    if len(stripped_line) < 3:
        return False
    if type is None:
        type = "<=" if "<->" in line else "="
    assert type in "<=", "type must be either '<' for '<->' or '=' for '==='"
    return all(char in type for char in stripped_line) and any(
        char * 3 in stripped_line for char in type
    )

def contains_image(line: str) -> bool:
    return bool(re.search(r"!\[.*?\]\(.*?\)", line))

def contains_deco(line: str) -> bool:
    return bool(re.match(r"^\s*@\(.*?\)\s*$", line))

def extract_title(document: str) -> Optional[str]:
    heading_pattern = r"^(#|##)\s+(.*?)(?:\n|$)"
    match = re.search(heading_pattern, document, re.MULTILINE)
    if match:
        return match.group(2).strip()
    else:
        return None

def rm_comments(document):
    document = re.sub(r"<!--[\s\S]*?-->", "", document)
    document = re.sub(r"^\s*%%.*$", "", document, flags=re.MULTILINE)
    return document.strip()