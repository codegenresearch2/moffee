import pytest
from moffee.compositor import composite, Direction, Type


@pytest.fixture
def sample_document():
    return \
"""
---
resource_dir: "resources"
default_h1: true
theme: beam
background-color: 'red'
---"
# Main Title

Other Pages
![Image-1](image.png)
---
Paragraph 1
===
Paragraph 2
<->
Paragraph 3
<->
![Image-2](image2.png)"
"""


def test_paginate_creates_correct_number_of_pages(sample_document):
    pages = composite(sample_document)
    assert len(pages) > 1, "Pagination should create multiple pages"


def test_frontmatter_parsing(sample_document):
    pages = composite(sample_document)
    assert pages[0].option.layout == "split"
    assert pages[0].option.default_h1 is True
    assert pages[0].option.styles == {"background-color": "red"}


def test_style_overwrite(sample_document):
    pages = composite(sample_document)
    assert pages[1].option.styles == {"background-color": "yellow"}
    assert pages[0].option.styles == {"background-color": "red"}

# Add more test functions as needed to cover other scenarios

if __name__ == "__main__":
    pytest.main()
