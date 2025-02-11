import copy
import re
import yaml
from typing import List, Optional, Tuple, Dict, Any

# Constants for default values
DEFAULT_ASPECT_RATIO = "16:9"
DEFAULT_SLIDE_WIDTH = 1280
DEFAULT_SLIDE_HEIGHT = 720

def is_empty(line: str) -> bool:
    """
    Check if a line is empty or contains only whitespace.
    """
    return line.strip() == ""

class PageOption:
    def __init__(self, default_h1: bool = False, default_h2: bool = True, default_h3: bool = True, 
                 theme: str = "default", layout: str = "content", resource_dir: str = ".", 
                 styles: dict = None):
        self.default_h1 = default_h1
        self.default_h2 = default_h2
        self.default_h3 = default_h3
        self.theme = theme
        self.layout = layout
        self.resource_dir = resource_dir
        self.styles = styles if styles is not None else {}

    def copy(self):
        """
        Create a shallow copy of the PageOption instance.
        """
        return copy.copy(self)

    @property
    def aspect_ratio(self):
        return self.styles.get("aspect_ratio", DEFAULT_ASPECT_RATIO)

    @property
    def slide_width(self):
        return self.styles.get("slide_width", DEFAULT_SLIDE_WIDTH)

    @property
    def slide_height(self):
        return self.styles.get("slide_height", DEFAULT_SLIDE_HEIGHT)

    @property
    def computed_slide_size(self):
        ratio_parts = self.aspect_ratio.split(":")
        if len(ratio_parts) == 2 and all(part.isdigit() for part in ratio_parts):
            try:
                width = int(self.slide_width)
                height = int(width * int(ratio_parts[1]) / int(ratio_parts[0]))
                return (width, height)
            except ValueError as e:
                raise ValueError("Invalid aspect ratio format or dimensions") from e
        raise ValueError("Invalid aspect ratio format")

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

class Chunk:
    def __init__(self, paragraph: Optional[str] = None, children: Optional[List["Chunk"]] = None, 
                 direction: Direction = Direction.HORIZONTAL, type: Type = Type.PARAGRAPH, 
                 alignment: Alignment = Alignment.LEFT):
        self.paragraph = paragraph
        self.children = children if children is not None else []
        self.direction = direction
        self.type = type
        self.alignment = alignment

class Page:
    def __init__(self, raw_md: str, option: PageOption, h1: Optional[str] = None, h2: Optional[str] = None, h3: Optional[str] = None):
        self.raw_md = raw_md
        self.option = option
        self.h1 = h1
        self.h2 = h2
        self.h3 = h3

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
        def split_by_div(text, type) -> List[Chunk]:
            strs = [""]
            current_escaped = False
            for line in text.split("\n"):
                if line.strip().startswith(""):
                    current_escaped = not current_escaped
                if is_divider(line, type) and not current_escaped:
                    strs.append("\n")
                else:
                    strs[-1] += line + "\n"
            return [Chunk(paragraph=s) for s in strs]

        vchunks = split_by_div(self.raw_md, "_")
        for i in range(len(vchunks)):
            hchunks = split_by_div(vchunks[i].paragraph, "*")
            if len(hchunks) > 1:
                vchunks[i] = Chunk(children=hchunks, type=Type.NODE)

        if len(vchunks) == 1:
            return vchunks[0]

        return Chunk(children=vchunks, direction=Direction.VERTICAL, type=Type.NODE)

def rm_comments(document):
    document = re.sub(r"<!--[\s\S]*?-->", "", document)
    document = re.sub(r"^\s*%%.*$", "", document, flags=re.MULTILINE)
    return document.strip()

def get_header_level(line):
    match = re.match(r"^(#{1,6})\s", line)
    if match:
        return len(match.group(1))
    else:
        return 0

def is_divider(line, type=None):
    stripped_line = line.strip()
    if len(stripped_line) < 3:
        return False
    if type is None:
        type = "-*_"

    assert type in "-*_", "type must be either '*', '-' or '_'"
    return all(char in type for char in stripped_line) and any(char * 3 in stripped_line for char in type)

def contains_deco(line):
    return bool(re.match(r"^\s*@\(.*?)\s*$", line))

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
        nonlocal current_page_lines, current_h1, current_h2, current_h3, options
        if all(is_empty(l) for l in current_page_lines):
            return

        raw_md = ""
        local_option = options.copy()
        for line in current_page_lines:
            if contains_deco(line):
                local_option = parse_deco(line, local_option)
            else:
                raw_md += "\n" + line

        page = Page(
            raw_md=raw_md,
            option=local_option,
            h1=current_h1,
            h2=current_h2,
            h3=current_h3,
        )

        pages.append(page)
        current_page_lines = []
        current_h1 = current_h2 = current_h3 = None

    for _, line in enumerate(lines):
        if line.strip().startswith(""):
            current_escaped = not current_escaped

        header_level = get_header_level(line) if not current_escaped else 0

        if header_level > 0 and (prev_header_level == 0 or prev_header_level >= header_level):
            create_page()

        if is_divider(line, type="-") and not current_escaped:
            create_page()
            continue

        current_page_lines.append(line)

        if header_level == 1:
            current_h1 = line.lstrip("#").strip()
        elif header_level == 2:
            current_h2 = line.lstrip("#").strip()
        elif header_level == 3:
            current_h3 = line.lstrip("#").strip()
        else:
            pass

        if header_level > 0:
            prev_header_level = header_level
        if header_level == 0 and not is_empty(line) and not contains_deco(line):
            prev_header_level = 0

    create_page()

    env_h1 = env_h2 = env_h3 = None
    for page in pages:
        inherit_h1 = page.option.default_h1
        inherit_h2 = page.option.default_h2
        inherit_h3 = page.option.default_h3
        if page.h1 is not None:
            env_h1 = page.h1
            env_h2 = env_h3 = None
            inherit_h1 = inherit_h2 = inherit_h3 = False
        if page.h2 is not None:
            env_h2 = page.h2
            env_h3 = None
            inherit_h2 = inherit_h3 = False
        if page.h3 is not None:
            env_h3 = page.h3
            inherit_h3 = False
        if inherit_h1:
            page.h1 = env_h1
        if inherit_h2:
            page.h2 = env_h2
        if inherit_h3:
            page.h3 = env_h3

    return pages

def parse_frontmatter(document: str) -> Tuple[str, PageOption]:
    document = document.strip()
    front_matter = ""
    content = document

    if document.startswith("---"):
        parts = document.split("---", 2)
        if len(parts) >= 3:
            front_matter = parts[1].strip()
            content = parts[2].strip()

    try:
        yaml_data = yaml.safe_load(front_matter) if front_matter else {}
    except yaml.YAMLError:
        yaml_data = {}

    option = PageOption(default_h1=yaml_data.get("default_h1", False),
                        default_h2=yaml_data.get("default_h2", True),
                        default_h3=yaml_data.get("default_h3", True),
                        theme=yaml_data.get("theme", "default"),
                        layout=yaml_data.get("layout", "content"),
                        resource_dir=yaml_data.get("resource_dir", "."),
                        styles=yaml_data.get("styles", {}))

    return content, option

def parse_deco(line: str, base_option: Optional[PageOption] = None) -> PageOption:
    def rm_quotes(s):
        if (s.startswith('"') and s.endswith('"')) or (
            s.startswith("'") and s.endswith("'")
        ):
            return s[1:-1]
        return s

    deco_match = re.match(r"^\s*@\((.*?)\)\s*$", line)
    if not deco_match:
        raise ValueError(f"Input line should contain a deco, {line} received.")

    deco_content = deco_match.group(1)
    pairs = re.findall(r"([\w\-]+)\s*=\s*([^,]+)(?:,|$)", deco_content)
    deco = {key.strip(): rm_quotes(value.strip()) for key, value in pairs}

    if base_option is None:
        base_option = PageOption()

    updated_option = base_option.copy()

    for key, value in deco.items():
        if hasattr(updated_option, key):
            setattr(updated_option, key, parse_value(value))
        else:
            updated_option.styles[key] = parse_value(value)

    return updated_option

def parse_value(value: str):
    if value.lower() == "true":
        return True
    elif value.lower() == "false":
        return False
    elif value.isdigit():
        return int(value)
    elif value.replace(".", "", 1).isdigit():
        return float(value)
    return value