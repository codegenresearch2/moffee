from typing import List, Tuple\nfrom dataclasses import dataclass, field, fields\nfrom typing import List, Optional, Dict, Any\nfrom copy import deepcopy\nimport yaml\nimport re\nfrom moffee.utils.md_helper import (\n    get_header_level,\n    is_divider,\n    is_empty,\n    rm_comments,\n    contains_deco)\n\n# Constants for default values\nDEFAULT_ASPECT_RATIO = "16:9"\nDEFAULT_SLIDE_WIDTH = 720\nDEFAULT_SLIDE_HEIGHT = 405\n\n@dataclass\nclass PageOption:\n    default_h1: bool = False\n    default_h2: bool = True\n    default_h3: bool = True\n    theme: str = "default"\n    layout: str = "content"\n    resource_dir: str = "."\n    aspect_ratio: str = DEFAULT_ASPECT_RATIO\n    slide_width: int = DEFAULT_SLIDE_WIDTH\n    slide_height: int = DEFAULT_SLIDE_HEIGHT\n    styles: dict = field(default_factory=dict)\n\n    @property\n    def computed_slide_size(self) -> Tuple[int, int]:\n        """\n        Calculate the slide size based on the aspect ratio, width, and height.\n        """\n        if not re.match(r"^\\d+:\\d+", self.aspect_ratio):\n            raise ValueError("Aspect ratio must be in the format of 'width:height')")\n        width_ratio = int(self.aspect_ratio.split(":")[0])\n        height_ratio = int(self.aspect_ratio.split(":")[1])\n        return (self.slide_width, int(self.slide_width / width_ratio * height_ratio))\n\nclass Direction:\n    HORIZONTAL = "horizontal"\n    VERTICAL = "vertical"\n\nclass Type:\n    PARAGRAPH = "paragraph"\n    NODE = "node"\n\nclass Alignment:\n    LEFT = "left"\n    CENTER = "center"\n    RIGHT = "right"\n    JUSTIFY = "justify"\n\n@dataclass\nclass Chunk:\n    paragraph: Optional[str] = None\n    children: Optional[List["Chunk"]] = field(default_factory=list)  # List of chunks\n    direction: Direction = Direction.HORIZONTAL\n    type: Type = Type.PARAGRAPH\n    alignment: Alignment = Alignment.LEFT\n\n@dataclass\nclass Page:\n    raw_md: str\n    option: PageOption\n    h1: Optional[str] = None\n    h2: Optional[str] = None\n    h3: Optional[str] = None\n\n    def __post_init__(self):\n        self._preprocess()\n\n    @property\n    def title(self) -> Optional[str]:\n        return self.h1 or self.h2 or self.h3\n\n    @property\n    def subtitle(self) -> Optional[str]:\n        if self.h1:\n            return self.h2 or self.h3\n        elif self.h2:\n            return self.h3\n        return None\n\n    @property\n    def chunk(self) -> Chunk:\n        """\n        Split raw_md into chunk tree\n        Chunk tree branches when in-page divider is met.\n        - adjacent "***"s create chunk with horizontal direction\n        - adjacent "___" create chunk with vertical direction\n        "___" possesses higher priority than "***"\n        """\n        # Implementation of chunk splitting logic\n    def _preprocess(self):\n        """\n        Additional processing needed for the page.\n        Modifies raw_md in place.\n        """\n        lines = self.raw_md.split("\n")\n        # Remove headings 1-3\n        lines = [l for l in lines if not (1 <= get_header_level(l) <= 3)]\n        self.raw_md = "\n".join(lines).strip()\n