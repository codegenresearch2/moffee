from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass, field, fields
from copy import deepcopy
import yaml
import re
from moffee.utils.md_helper import (
    get_header_level,
    is_divider,
    is_empty,
    rm_comments,
    contains_deco,
)

@dataclass
class PageOption:
    default_h1: bool = False
    default_h2: bool = True
    default_h3: bool = True
    theme: str = "default"
    layout: str = "content"
    resource_dir: str = "."
    styles: dict = field(default_factory=dict)
    width: int = 1920
    height: int = 1080

class Direction:
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"

class Type:
    PARAGRAPH = "paragraph"
    NODE = "node"

class Alignment:
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    JUSTIFY = "justify"

@dataclass
class Chunk:
    paragraph: Optional[str] = None
    children: Optional[List["Chunk"]] = field(default_factory=list)  # List of chunks
    direction: Direction = Direction.HORIZONTAL
    type: Type = Type.PARAGRAPH
    alignment: Alignment = Alignment.LEFT

@dataclass
class Page:
    raw_md: str
    option: PageOption
    h1: Optional[str] = None
    h2: Optional[str] = None
    h3: Optional[str] = None

    def __post_init__(self):
        self._preprocess()

    @property
    def title(self) -> Optional[str]:
        return self.h1 or self.h2 or self.h3

    @property
    def subtitle(self) -> Optional[str]:
        if self.h1:
            return self.h2 or self.h3
        elif self.h2:
            return self.h3
        return None

    @property
    def chunk(self) -> Chunk:
        # ... (same as before)

    def _preprocess(self):
        # ... (same as before)

def parse_frontmatter(document: str) -> Tuple[str, PageOption]:
    # ... (same as before)

def parse_deco(line: str, base_option: Optional[PageOption] = None) -> PageOption:
    # ... (same as before)

def parse_value(value: str):
    # ... (same as before)

def composite(document: str) -> List[Page]:
    pages: List[Page] = []
    current_page_lines = []
    current_escaped = False
    current_h1 = current_h2 = current_h3 = None
    prev_header_level = 0

    document = rm_comments(document)
    document, options = parse_frontmatter(document)

    lines = document.split("\n")

    def create_page():
        # ... (same as before)

    for _, line in enumerate(lines):
        # ... (same as before)

    # ... (same as before)

    for page in pages:
        # Enhance error handling for aspect ratios
        if page.option.width <= 0 or page.option.height <= 0:
            raise ValueError("Width and height must be positive integers.")

    return pages

This code has been updated to include slide dimensions in the PageOption class, and it now raises an error if the width or height is not a positive integer. The code structure and readability have been maintained.