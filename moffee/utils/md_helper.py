import re
from typing import Optional


def is_comment(line: str) -> bool:
    """\n    Determines if a given line is a Markdown comment.\n    Markdown comments are in the format <!-- comment -->\n\n    :param line: The line to check\n    :return: True if the line is a comment, False otherwise\n    """
    return bool(re.match(r"^\s*<!--.*-->\s*$", line))


def get_header_level(line: str) -> int:
    """\n    Determines the header level of a given line.\n\n    :param line: The line to check\n    :return: The header level (1-6) if it's a header, 0 otherwise\n    """
    match = re.match(r"^(#{1,6})\s", line)
    if match:
        return len(match.group(1))
    else:
        return 0


def is_empty(line: str) -> bool:
    """\n    Determines if a given line is an empty line in markdown.\n    A line is empty if it is blank or comment only\n\n    :param line: The line to check\n    :return: True if the line is empty, False otherwise\n    """
    return is_comment(line) or line.strip() == ""


def is_divider(line: str, type=None) -> bool:
    """\n    Determines if a given line is a Markdown divider (horizontal rule).\n    Markdown dividers are three or more hyphens, asterisks, or underscores,\n    without any other characters except spaces.\n\n    :param line: The line to check\n    :param type: Which type to match, str. e.g. "*" to match "***" only. Defaults to "", match any of "*", "-" and "_".\n    :return: True if the line is a divider, False otherwise\n    """
    stripped_line = line.strip()
    if len(stripped_line) < 3:
        return False
    if type is None:
        type = "-*_"

    assert type in "-*_", "type must be either '*', '-' or '_'"
    return all(char in type for char in stripped_line) and any(
        char * 3 in stripped_line for char in type
    )


def contains_image(line: str) -> bool:
    """\n    Determines if a given line contains a Markdown image.\n    Markdown images are in the format ![alt text](image_url)\n\n    :param line: The line to check\n    :return: True if the line contains an image, False otherwise\n    """
    return bool(re.search(r"!\[.*?\]\(.*?\)", line))


def contains_deco(line: str) -> bool:
    """\n    Determines if a given line contains a deco (custom decorator).\n    Decos are in the format @(key1=value1, key2=value2, ...)\n\n    :param line: The line to check\n    :return: True if the line contains a deco, False otherwise\n    """
    return bool(re.match(r"^\s*@\(.*?\)\s*$", line))


def extract_title(document: str) -> Optional[str]:
    """\n    Extracts proper title from document.\n    The title should be the first-occurred level 1 or 2 heading.\n\n    :param document: The document in markdown\n    :return: title if there is one, otherwise None\n    """
    heading_pattern = r"^(#|##)\s+(.*?)(?:\n|$)"
    match = re.search(heading_pattern, document, re.MULTILINE)

    if match:
        return match.group(2).strip()
    else:
        return None


def rm_comments(document):
    """\n    Remove comments from markdown. Supports html and "%%"\n    """
    document = re.sub(r"<!--[\s\S]*?-->", "", document)
    document = re.sub(r"^\s*%%.*$", "", document, flags=re.MULTILINE)

    return document.strip()