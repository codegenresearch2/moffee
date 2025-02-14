import pytest
from moffee.compositor import composite, Direction, Type
import re

def is_divider(line: str, type: str = None) -> bool:
    if type is None:
        return re.match(r'^\s*(---|\*\*\*|\+\+\+)\s*$', line) is not None
    else:
        divider_map = {'-': '---', '*': '***', '<': '<->', '=': '==='}
        return line.strip() == divider_map[type]

def rm_comments(document: str) -> str:
    lines = document.split('\n')
    return '\n'.join([line for line in lines if not line.strip().startswith('<!--')])

def composite(document: str) -> List[Page]:
    # ... existing code ...
    def _preprocess(self):
        # ... existing code ...
        self.raw_md = '\n'.join([line for line in self.raw_md.splitlines() if not is_divider(line)]).strip()

def test_paginate_creates_correct_number_of_pages(sample_document):
    # ... existing code ...

def test_frontmatter_parsing(sample_document):
    # ... existing code ...

def test_style_overwrite(sample_document):
    # ... existing code ...

def test_header_inheritance():
    # ... existing code ...

def test_page_splitting_on_headers():
    # ... existing code ...

def test_page_splitting_on_dividers():
    doc = """\n    Content 1\n\n    Content 2\n\n    Content 3\n    """
    pages = composite(doc)
    assert len(pages) == 3

def test_escaped_area_paging():
    # ... existing code ...

def test_escaped_area_chunking():
    # ... existing code ...

def test_title_and_subtitle():
    # ... existing code ...

def test_adjacent_headings_same_level():
    # ... existing code ...

def test_chunking_trivial():
    # ... existing code ...

def test_chunking_vertical():
    # ... existing code ...

def test_chunking_horizontal():
    # ... existing code ...

def test_chunking_hybrid():
    # ... existing code ...

def test_empty_lines_handling():
    # ... existing code ...

def test_deco_handling():
    # ... existing code ...

def test_multiple_deco():
    # ... existing code ...

if __name__ == "__main__":
    pytest.main()