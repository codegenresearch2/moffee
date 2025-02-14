import os
from urllib.parse import urljoin, urlparse
import re
from typing import Optional

def is_comment(line: str) -> bool:
    """Determines if a given line is a Markdown comment."""
    return line.strip().startswith('<!--') and line.strip().endswith('-->')

def get_header_level(line: str) -> int:
    """Determines the header level of a given line."""
    if line.startswith('#'):
        return len(line.split(' ')[0])
    return 0

def is_empty(line: str) -> bool:
    """Determines if a given line is an empty line in markdown."""
    return line.strip() == '' or is_comment(line)

def is_divider(line: str, type: str = None) -> bool:
    """Determines if a given line is a Markdown divider."""
    stripped_line = line.strip()
    if len(stripped_line) < 3:
        return False
    if type is None:
        return stripped_line == '---' or stripped_line == '***' or stripped_line == '___'
    return stripped_line == type * 3

def contains_image(line: str) -> bool:
    """Determines if a given line contains a Markdown image."""
    return '![' in line and '](' in line

def contains_deco(line: str) -> bool:
    """Determines if a given line contains a deco (custom decorator)."""
    return line.strip().startswith('@(') and line.strip().endswith(')')

def extract_title(document: str) -> Optional[str]:
    """Extracts proper title from document."""
    match = re.search(r'^(#|##)\s+(.*?)$', document, re.MULTILINE)
    return match.group(2).strip() if match else None

def rm_comments(document: str) -> str:
    """Remove comments from markdown."""
    document = re.sub(r'<!--.*?-->', '', document, flags=re.DOTALL)
    document = re.sub(r'^%%.*$', '', document, flags=re.MULTILINE)
    return document.strip()