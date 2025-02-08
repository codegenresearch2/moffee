import pytest\nfrom moffee.compositor import composite, Direction, Type\n\n@pytest.fixture\ndef sample_document() -> str:\n    return '''\n---\nbackground-color: gray\nlayout: split\ndefault_h1: true\ndefault_h2: false\n---\n# Main Title\n\n## Subtitle\n\nContent of the first slide.\n\n---\n@(background-color=yellow)\n## Second Slide\n\n- Bullet point 1\n- Bullet point 2\n\n### Subheader\nMore content.\n![](Image.png)\n\n## Another Header\n### Consecutive Header\n\nNormal text here.\n\n# New Main Title\n\n1. Numbered list\n2. Second item\n3. Third item\n\nThis is a long paragraph\nIt continues for several lines to demonstrate the line count limit.\nWe'll add more lines to ensure it goes over the 12 non-empty lines limit.\nThis is line 4.\nThis is line 5.\nThis is line 6.\nThis is line 7.\nThis is line 8.\nThis is line 9.\nThis is line 10.\nThis is line 11.\nThis is line 12.'''\n\n@pytest.fixture\ndef sample_pages() -> list:\n    return composite(sample_document())\n\ndef test_paginate_creates_correct_number_of_pages(sample_pages):\n    assert len(sample_pages) > 1, 'Pagination should create multiple pages'\n\ndef test_frontmatter_parsing(sample_pages):\n    assert sample_pages[0].option.layout == 'split'\n    assert sample_pages[0].option.default_h1 is True\n    assert sample_pages[0].option.default_h2 is False\n    assert sample_pages[0].option.styles == {'background-color': 'gray'}\n\ndef test_style_overwrite(sample_pages):\n    assert sample_pages[1].option.styles == {'background-color': 'yellow'}\n    assert sample_pages[0].option.styles == {'background-color': 'gray'}\n\ndef test_header_inheritance():\n    doc = '''\n    # Main Title\n    Content\n    ## Subtitle\n    More content\n    ### Subheader\n    Even more content\n    '''\n    pages = composite(doc)\n    assert pages[0].h1 == 'Main Title'\n    assert pages[1].h2 == 'Subtitle'\n    assert pages[1].h3 == 'Subheader'\n\n# Add more test functions as needed to cover other scenarios\n