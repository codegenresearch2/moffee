import pytest
from moffee.utils.md_helper import (
    is_comment,
    is_empty,
    get_header_level,
    is_divider,
    contains_image,
    contains_deco,
    extract_title,
    rm_comments,
)


def test_is_comment(line: str) -> bool:
    """
    Determines if a given line is a Markdown comment.
    Markdown comments are in the format <!-- comment -->

    :param line: The line to check
    :return: True if the line is a comment, False otherwise
    """
    return bool(re.match(r"^\s*<!--.*-->\s*$", line))


def test_is_empty(line: str) -> bool:
    """
    Determines if a given line is an empty line in markdown.
    A line is empty if it is blank or comment only

    :param line: The line to check
    :return: True if the line is empty, False otherwise
    """
    return is_comment(line) or line.strip() == ""


def test_get_header_level(line: str) -> int:
    """
    Determines the header level of a given line.

    :param line: The line to check
    :return: The header level (1-6) if it's a header, 0 otherwise
    """
    match = re.match(r"^(#{1,6})\s", line)
    if match:
        return len(match.group(1))
    else:
        return 0


def test_is_divider(line: str, type: Optional[str] = None) -> bool:
    """
    Determines if a given line is a Markdown divider (horizontal rule, vertical divider, or horizontal divider).

    :param line: The line to check
    :param type: Which type to match, str. e.g. "*" to match "***" only, "<" to match "<->", "=" to match "===".
                 Defaults to None, match any of "*", "-", "_", "<" or "=".
    :return: True if the line is a divider, False otherwise
    """
    stripped_line = line.strip()
    if type is None:
        return bool(re.match(r"^\s*([\*\-\_]{3,}|<->|={3,})\s*$", stripped_line))
    elif type == "*":
        return bool(re.match(r"^\s*\*{3,}\s*$", stripped_line))
    elif type == "-":
        return bool(re.match(r"^\s*\-{3,}\s*$", stripped_line))
    elif type == "_":
        return bool(re.match(r"^\s*_{3,}\s*$", stripped_line))
    elif type == "<":
        return bool(re.match(r"^\s*<->\s*$", stripped_line))
    elif type == "=":
        return bool(re.match(r"^\s*={3,}\s*$", stripped_line))
    else:
        return False


def test_contains_image(line: str) -> bool:
    """
    Determines if a given line contains a Markdown image.
    Markdown images are in the format ![alt text](image_url)

    :param line: The line to check
    :return: True if the line contains an image, False otherwise
    """
    return bool(re.search(r"!\[.*?\]\(.*?\)", line))


def test_contains_deco(line: str) -> bool:
    """
    Determines if a given line contains a deco (custom decorator).
    Decos are in the format @(key1=value1, key2=value2, ...)

    :param line: The line to check
    :return: True if the line contains a deco, False otherwise
    """
    return bool(re.match(r"^\s*@\(.*?\)\s*$", line))


def test_extract_title(document: str) -> Optional[str]:
    """
    Extracts proper title from document.
    The title should be the first-occurred level 1 or 2 heading.

    :param document: The document in markdown
    :return: title if there is one, otherwise None
    """
    heading_pattern = r"^(#|##)\s+(.*?)(?:\n|$)"
    match = re.search(heading_pattern, document, re.MULTILINE)

    if match:
        return match.group(2).strip()
    else:
        return None


def test_rm_comments(document: str) -> str:
    """
    Remove comments from markdown. Supports html and "%%"
    """
    document = re.sub(r"<!--[\s\S]*?-->", "", document)
    document = re.sub(r"^\s*%%.*$", "", document, flags=re.MULTILINE)

    return document.strip()