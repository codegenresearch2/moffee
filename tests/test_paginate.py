import pytest
from mdbeamer.splitter import paginate

@pytest.fixture
def sample_document():
    return """
---
layout: split
default_h1: true
default_h2: false
---
# Main Title

## Subtitle

Content of the first slide.

---

## Second Slide

- Bullet point 1
- Bullet point 2

### Subheader
More content.
![](Image.png)

## Another Header
### Consecutive Header

Normal text here.

# New Main Title

1. Numbered list
2. Second item
3. Third item

This is a long paragraph that should trigger a new page due to line count.
It continues for several lines to demonstrate the line count limit.
We'll add more lines to ensure it goes over the 12 non-empty lines limit.
This is line 4.
This is line 5.
This is line 6.
This is line 7.
This is line 8.
This is line 9.
This is line 10.
This is line 11.
This is line 12.
This line should be on a new page.
    """

def test_paginate_creates_correct_number_of_pages(sample_document):
    pages = paginate(sample_document)
    assert len(pages) > 1, "Pagination should create multiple pages"

def test_frontmatter_parsing(sample_document):
    pages = paginate(sample_document)
    assert pages[0].option.layout == "split"
    assert pages[0].option.default_h1 == True
    assert pages[0].option.default_h2 == False

def test_header_inheritance():
    doc = """
# Main Title
Content
## Subtitle
More content
### Subheader
Even more content
    """
    pages = paginate(doc)
    assert pages[0].h1 == "Main Title"
    assert pages[1].h1 == None
    assert pages[1].h2 == "Subtitle"
    assert pages[2].h1 == None
    assert pages[2].h2 == "Subtitle"
    assert pages[2].h3 == "Subheader"

def test_page_splitting_on_headers():
    doc = """
# Header 1
Content 1
## Header 2
Content 2
# New Header 1
Content 3
    """
    pages = paginate(doc)
    assert len(pages) == 3
    assert pages[0].h1 == "Header 1"
    assert pages[1].h2 == "Header 2"
    assert pages[2].h1 == "New Header 1"

def test_page_splitting_on_dividers():
    doc = """
Content 1
---
Content 2
***
Content 3
    """
    pages = paginate(doc)
    assert len(pages) == 3

def test_chunking():
    doc = """
Paragraph 1

Paragraph 2
![](image.jpg)
Paragraph 3


Paragraph 4
    """
    pages = paginate(doc)
    chunks = pages[0].chunks
    assert len(chunks) == 4
    assert chunks[1].type == "image"

def test_title_and_subtitle():
    doc = """
# Title
## Subtitle
# Title2
#### Heading4
### Heading3
Content
    """
    pages = paginate(doc)
    assert len(pages) == 2
    assert pages[0].title == "Title"
    assert pages[0].subtitle == "Subtitle"
    assert pages[1].title == "Title2"

def test_empty_lines_handling():
    doc = """
# Title

Content with empty line above
    """
    pages = paginate(doc)
    assert len(pages[0].chunks) == 1
    assert pages[0].deco == {}

def test_image_handling():
    doc = """
# Title
![Alt text](image.jpg)
Content after image
    """
    pages = paginate(doc)
    assert any(chunk.type == "image" for chunk in pages[0].chunks)

def test_deco_handling():
    doc = """
---
default_h1: true
---
# Title
@(default_h1=false)
Hello
@(background=blue)
"""
    pages = paginate(doc)
    assert pages[0].raw_md == 'Hello'
    assert pages[0].option.default_h1 == False
    assert pages[0].deco == {'background': 'blue'}
    
def test_multiple_deco():
    doc = """
---
default_h1: true
---
# Title1
@(background=blue)
## Title2
# Title
@(default_h1=false)
Hello
"""
    pages = paginate(doc)
    assert len(pages) == 2
    assert pages[0].raw_md == ''
    assert pages[0].title == 'Title1'
    assert pages[0].subtitle == 'Title2'
    assert pages[0].deco == {'background': 'blue'}
    assert pages[0].option.default_h1 == True
    assert pages[1].option.default_h1 == False
    assert pages[1].chunks[0].content == 'Hello'
    
    

if __name__ == "__main__":
    pytest.main()