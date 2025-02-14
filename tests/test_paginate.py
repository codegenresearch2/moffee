import pytest
from moffee.compositor import composite, Direction, Type


@pytest.fixture
def sample_document():
    return """\n---\nbackground-color: gray\nlayout: split\ndefault_h1: true\ndefault_h2: false\n---\n# Main Title\n\n## Subtitle\n\nContent of the first slide.\n\n---\n@(background-color=yellow)\n## Second Slide\n\n- Bullet point 1\n- Bullet point 2\n\n### Subheader\nMore content.\n![](Image.png)\n\n## Another Header\n### Consecutive Header\n\nNormal text here.\n\n# New Main Title\n\n1. Numbered list\n2. Second item\n3. Third item\n\nThis is a long paragraph\nIt continues for several lines to demonstrate the line count limit.\nWe'll add more lines to ensure it goes over the 12 non-empty lines limit.\nThis is line 4.\nThis is line 5.\nThis is line 6.\nThis is line 7.\nThis is line 8.\nThis is line 9.\nThis is line 10.\nThis is line 11.\nThis is line 12.\n    """


def test_paginate_creates_correct_number_of_pages(sample_document):
    pages = composite(sample_document)
    assert len(pages) > 1, "Pagination should create multiple pages"


def test_frontmatter_parsing(sample_document):
    pages = composite(sample_document)
    assert pages[0].option.layout == "split"
    assert pages[0].option.default_h1 is True
    assert pages[0].option.default_h2 is False
    assert pages[0].option.styles == {"background-color": "gray"}


def test_style_overwrite(sample_document):
    pages = composite(sample_document)
    assert pages[1].option.styles == {"background-color": "yellow"}
    assert pages[0].option.styles == {"background-color": "gray"}


def test_header_inheritance():
    doc = """\n# Main Title\nContent\n## Subtitle\nMore content\n### Subheader\nEven more content\n    """
    pages = composite(doc)
    assert pages[0].h1 == "Main Title"
    assert pages[1].h1 is None
    assert pages[1].h2 == "Subtitle"
    assert pages[2].h1 is None
    assert pages[2].h2 == "Subtitle"
    assert pages[2].h3 == "Subheader"


def test_page_splitting_on_headers():
    doc = """\n# Header 1\nContent 1\n## Header 2\nContent 2\n# New Header 1\nContent 3\n    """
    pages = composite(doc)
    assert len(pages) == 3
    assert pages[0].h1 == "Header 1"
    assert pages[1].h2 == "Header 2"
    assert pages[2].h1 == "New Header 1"


def test_page_splitting_on_dividers():
    doc = """\nContent 1\n---\nContent 2\n***\nContent 3\n    """
    pages = composite(doc)
    assert len(pages) == 2


def test_escaped_area_paging():
    doc = """\nContent 1\nbash\n---\nContent 2\n\n***\nContent 3\n    """
    pages = composite(doc)
    assert len(pages) == 1


def test_escaped_area_chunking():
    doc = """\nContent 1\n---\nContent 2\nbash\n***\nContent 3\n\n    """
    pages = composite(doc)
    assert len(pages) == 2
    assert len(pages[1].chunk.children) == 0


def test_title_and_subtitle():
    doc = """\n# Title\n## Subtitle\n# Title2\n#### Heading4\n### Heading3\nContent\n    """
    pages = composite(doc)
    assert len(pages) == 2
    assert pages[0].title == "Title"
    assert pages[0].subtitle == "Subtitle"
    assert pages[1].title == "Title2"


def test_adjacent_headings_same_level():
    doc = """\n# Title\n## Subtitle\n## Subtitle2\n### Heading\n### Heading2\n"""
    pages = composite(doc)
    assert len(pages) == 3
    assert pages[1].title == "Subtitle2"
    assert pages[1].subtitle == "Heading"


def test_chunking_trivial():
    doc = """\nParagraph 1\n\nParagraph 2\n![](image.jpg)\nParagraph 3\n\nParagraph 4\n    """
    pages = composite(doc)
    chunk = pages[0].chunk
    assert chunk.type == Type.PARAGRAPH
    assert len(chunk.children) == 0
    assert chunk.paragraph.strip() == doc.strip()


def test_chunking_vertical():
    doc = """\nParagraph 1\n___\n\nParagraph 2\n    """
    pages = composite(doc)
    chunk = pages[0].chunk
    assert chunk.type == Type.NODE
    assert len(chunk.children) == 2
    assert chunk.direction == Direction.VERTICAL
    assert chunk.children[0].type == Type.PARAGRAPH


def test_chunking_horizontal():
    doc = """\nParagraph 1\n***\n\nParagraph 2\n***\n    """
    pages = composite(doc)
    chunk = pages[0].chunk
    assert chunk.type == Type.NODE
    assert len(chunk.children) == 3
    assert chunk.direction == Direction.HORIZONTAL
    assert chunk.children[0].type == Type.PARAGRAPH


def test_chunking_hybrid():
    doc = """\nOther Pages\n---\nParagraph 1\n___\nParagraph 2\n***\nParagraph 3\n***\nParagraph 4\n    """
    pages = composite(doc)
    assert len(pages) == 2
    chunk = pages[1].chunk
    assert chunk.type == Type.NODE
    assert len(chunk.children) == 2
    assert chunk.direction == Direction.VERTICAL
    assert len(chunk.children[0].children) == 0
    assert chunk.children[0].type == Type.PARAGRAPH
    assert chunk.children[0].paragraph.strip() == "Paragraph 1"
    next = chunk.children[1]
    assert next.direction == Direction.HORIZONTAL
    assert len(next.children) == 3


def test_empty_lines_handling():
    doc = """\n# Title\n\nContent with empty line above\n    """
    pages = composite(doc)
    assert len(pages[0].chunk.children) == 0
    assert pages[0].option.styles == {}


def test_deco_handling():
    doc = """\n---\ndefault_h1: true\n---\n# Title\n@(default_h1=false)\nHello\n@(background=blue)\n"""
    pages = composite(doc)
    assert pages[0].raw_md == "Hello"
    assert pages[0].option.default_h1 is False
    assert pages[0].option.styles == {"background": "blue"}


def test_multiple_deco():
    doc = """\n---\ndefault_h1: true\n---\n# Title1\n@(background=blue)\n## Title2\n# Title\n@(default_h1=false)\nHello\n"""
    pages = composite(doc)
    assert len(pages) == 2
    assert pages[0].raw_md == ""
    assert pages[0].title == "Title1"
    assert pages[0].subtitle == "Title2"
    assert pages[0].option.styles == {"background": "blue"}
    assert pages[0].option.default_h1 is True
    assert pages[1].option.default_h1 is False


if __name__ == "__main__":
    pytest.main()