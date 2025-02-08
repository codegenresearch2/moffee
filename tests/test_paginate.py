import pytest
from moffee.compositor import composite, Direction, Type


@pytest.fixture
def sample_document():
    return \
"""
---resource_dir: resources\ndefault_h1: true\ndefault_h2: false\nlayout: split\ntheme: beam\nbackground-color: 'red'\n---"
# Main Title\n\nOther Pages\n![Image-1](image.png)\n---\nParagraph 1\n===\nParagraph 2\n<->\nParagraph 3\n<->\n![Image-2](image2.png)"


def test_paginate_creates_correct_number_of_pages(sample_document):
    pages = composite(sample_document)
    assert len(pages) > 1, 'Pagination should create multiple pages'


def test_frontmatter_parsing(sample_document):
    pages = composite(sample_document)
    assert pages[0].option.layout == 'split', 'Expected layout to be split'
    assert pages[0].option.default_h1 is True, 'Expected default_h1 to be True'
    assert pages[0].option.default_h2 is False, 'Expected default_h2 to be False'
    assert pages[0].option.styles == {'background-color': 'red'}, 'Expected background color to be red'


def test_style_overwrite(sample_document):
    pages = composite(sample_document)
    assert pages[1].option.styles == {'background-color': 'yellow'}, 'Expected background color to be yellow'
    assert pages[0].option.styles == {'background-color': 'red'}, 'Expected original background color to be red'

# Add more test functions as needed to cover other scenarios

if __name__ == '__main__':
    pytest.main()