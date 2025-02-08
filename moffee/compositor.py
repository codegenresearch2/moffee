from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass, field
import yaml
import re
from copy import deepcopy

DEFAULT_ASPECT_RATIO = '16:9'
DEFAULT_SLIDE_WIDTH = 720
DEFAULT_SLIDE_HEIGHT = 405

@dataclass
class PageOption:
    default_h1: bool = False
    default_h2: bool = True
    default_h3: bool = True
    theme: str = 'default'
    aspect_ratio: str = DEFAULT_ASPECT_RATIO
    slide_width: int = DEFAULT_SLIDE_WIDTH
    slide_height: int = DEFAULT_SLIDE_HEIGHT
    layout: str = 'content'
    resource_dir: str = '.'
    styles: dict = field(default_factory=dict)

    @property
    def computed_slide_size(self) -> Tuple[int, int]:
        changed_ar = self.aspect_ratio != DEFAULT_ASPECT_RATIO
        changed_w = self.slide_width != DEFAULT_SLIDE_WIDTH
        changed_h = self.slide_height != DEFAULT_SLIDE_HEIGHT

        assert isinstance(self.aspect_ratio, str), f'Aspect ratio must be a string, got {self.aspect_ratio}'
        matches = re.match('([0-9]+):([0-9]+)', self.aspect_ratio)
        if matches is None:
            raise ValueError(f'Incorrect aspect ratio format: {self.aspect_ratio}')
        ar = int(matches.group(2)) / int(matches.group(1))
        width = self.slide_width
        height = self.slide_height

        if changed_ar and changed_h and changed_w:
            raise ValueError(
                f'Aspect ratio, width and height cannot be changed at the same time!')
        if changed_ar and changed_h:
            width = height / ar
        elif changed_ar and changed_w:
            height = width * ar
        elif changed_ar:
            height = width * ar

        return width, height

class Direction:
    HORIZONTAL = 'horizontal'
    VERTICAL = 'vertical'

class Type:
    PARAGRAPH = 'paragraph'
    NODE = 'node'

@dataclass
class Chunk:
    paragraph: Optional[str] = None
    children: Optional[List['Chunk']] = field(default_factory=list)
    direction: Direction = Direction.HORIZONTAL
    type: Type = Type.PARAGRAPH
    alignment: str = 'left'  # Added alignment attribute

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
        lines = self.raw_md.split('\n')
        chunks = []
        current_chunk = Chunk()
        for line in lines:
            if line.strip().startswith('#'):
                if current_chunk.paragraph:
                    chunks.append(current_chunk)
                    current_chunk = Chunk()
            current_chunk.paragraph = (current_chunk.paragraph + '\n' + line) if current_chunk.paragraph else line
        if current_chunk.paragraph:
            chunks.append(current_chunk)
        return Chunk(children=chunks, direction=Direction.VERTICAL, type=Type.NODE)

    def _preprocess(self):
        lines = self.raw_md.split('\n')
        lines = [l for l in lines if not (1 <= get_header_level(l) <= 3)]
        self.raw_md = '\n'.join(lines).strip()


def parse_frontmatter(document: str) -> Tuple[str, PageOption]:
    document = document.strip()
    front_matter = ''
    content = document

    if document.startswith('---\n'):
        parts = document.split('---\n', 2)
        if len(parts) >= 3:
            front_matter = parts[1].strip()
            content = parts[2].strip()

    try:
        yaml_data = yaml.safe_load(front_matter) if front_matter else {}
    except yaml.YAMLError:
        yaml_data = {}

    option = PageOption()
    for field in fields(option):
        name = field.name
        if name in yaml_data:
            setattr(option, name, yaml_data.pop(name))
    option.styles = yaml_data

    return content, option


def parse_deco(line: str, base_option: PageOption = None) -> PageOption:
    def parse_key_value_string(s: str) -> dict:
        pattern = r'([